open System
open System.IO
open System.Collections
open System.Collections.Generic
open System.Reflection
open System.Text.Json
open Microsoft.FSharp.Reflection
open FSharp.Compiler.CodeAnalysis
open FSharp.Compiler.Syntax
open FSharp.Compiler.Text
open CodeAgent.DotNet

let checker = FSharpChecker.Create()
let fields (value: obj) =
    if isNull value then "", Map.empty else
    let t = value.GetType()
    if FSharpType.IsUnion(t, true) then
        let case, vals = FSharpValue.GetUnionFields(value, t, true)
        case.Name, Array.zip (case.GetFields() |> Array.map (fun p -> p.Name)) vals |> Map.ofArray
    elif FSharpType.IsRecord(t, true) then
        t.Name, Array.zip (FSharpType.GetRecordFields(t, true) |> Array.map (fun p -> p.Name)) (FSharpValue.GetRecordFields(value, true)) |> Map.ofArray
    else t.Name, Map.empty

let get key (m: Map<string,obj>) = m.TryFind key |> Option.defaultValue null
let rec ident (o: obj) =
    match o with
    | null -> ""
    | :? Ident as i -> i.idText
    | :? SynLongIdent as i -> i.LongIdent |> List.map (fun x -> x.idText) |> String.concat "."
    | :? SynIdent as i -> let (SynIdent(id, _)) = i in id.idText
    | :? IEnumerable as xs -> xs |> Seq.cast<obj> |> Seq.map ident |> Seq.filter ((<>) "") |> String.concat "."
    | _ -> ""

let rec exprName (o: obj) =
    let kind, f = fields o
    match kind with
    | "Ident" -> ident (get "ident" f)
    | "LongIdent" -> ident (get "longDotId" f)
    | "DotGet" -> exprName (get "expr" f) + "." + ident (get "longDotId" f)
    | "App" -> exprName (get "funcExpr" f)
    | "TypeApp" | "Paren" -> exprName (get "expr" f)
    | "New" ->
        let _, typ = fields (get "targetType" f)
        ident (get "longDotId" typ)
    | _ -> ""

let walk _ (root: obj) (visit: obj -> unit) =
    let pending = Stack<obj>()
    pending.Push(root)
    let mutable count = 0
    while pending.Count > 0 do
        count <- count + 1
        if count > 1000000 then failwith "F# syntax tree exceeded the analysis node budget"
        let o = pending.Pop()
        if not (isNull o) then
            let t = o.GetType()
            if o :? string || t.IsPrimitive || t.IsEnum then () else
            visit o
            if FSharpType.IsUnion(t, true) then
                let _, values = FSharpValue.GetUnionFields(o, t, true)
                values |> Array.iter pending.Push
            elif FSharpType.IsRecord(t, true) then
                FSharpValue.GetRecordFields(o, true) |> Array.iter pending.Push
            elif o :? IEnumerable then
                (o :?> IEnumerable) |> Seq.cast<obj> |> Seq.iter pending.Push

let fsharpScan (path: string) (code: string) (profile:string) =
    let options = { FSharpParsingOptions.Default with SourceFiles=[|path|]; IsInteractive=path.EndsWith(".fsx"); ApplyLineDirectives=false }
    let parsed = checker.ParseFile(path, SourceText.ofString code, options) |> Async.RunSynchronously
    let errors = List<string>()
    parsed.Diagnostics |> Array.filter (fun d -> d.Severity = FSharp.Compiler.Diagnostics.FSharpDiagnosticSeverity.Error) |> Array.iter (fun d -> errors.Add(d.ToString()))
    let nodes = ResizeArray<SynExpr>()
    let scopes = ResizeArray<range>()
    let bindingNodes = ResizeArray<SynBinding>()
    let typedParameters = ResizeArray<obj * range>()
    let lambdaNodes = ResizeArray<SynExpr>()
    let bindings = ResizeArray<string * obj * range * range>()
    let contains (outer:range) (inner:range) = (outer.StartLine,outer.StartColumn) <= (inner.StartLine,inner.StartColumn) && (outer.EndLine,outer.EndColumn) >= (inner.EndLine,inner.EndColumn)
    let width (r:range) = (r.EndLine-r.StartLine)*100000 + r.EndColumn-r.StartColumn
    let whole = Range.mkRange path (Position.mkPos 0 0) (Position.mkPos (code.Split('\n').Length+1) 0)
    scopes.Add(whole)
    let opens = ResizeArray<string * range>()
    let aliases = ResizeArray<string * string * range>()
    let shadows = ResizeArray<string * range>()
    let sourceRange fields = match get "range" fields with :? range as r -> r | _ -> whole
    walk 0 (box parsed.ParseTree) (fun o ->
        match o with
        | :? SynExpr as e ->
            nodes.Add(e)
            let kind,_=fields o
            if kind="LetOrUse" || kind="Lambda" then scopes.Add(e.Range)
            if kind="Lambda" then lambdaNodes.Add(e)
        | :? SynModuleOrNamespace as m -> scopes.Add(m.Range)
        | :? SynBinding as b ->
            bindingNodes.Add(b)
            let _, bf=fields o
            let pk,_=fields (get "headPat" bf)
            if pk="LongIdent" then
                match get "expr" bf with
                | :? SynExpr as expr -> scopes.Add(expr.Range)
                | _ -> ()
        | _ -> ()
        let kind, f = fields o
        if kind = "NestedModule" then scopes.Add(sourceRange f)
        if kind = "Open" then
            let k, t = fields (get "target" f)
            if k = "ModuleOrNamespace" then opens.Add(ident (get "longId" t),sourceRange f)
        if kind = "SynTypeDefn" then
            let _, info = fields (get "typeInfo" f)
            let name = ident (get "longId" info)
            let rk, repr = fields (get "typeRepr" f)
            if rk = "Simple" then
                let sk, simple = fields (get "simpleRepr" repr)
                if sk = "TypeAbbrev" then
                    let _, rhs = fields (get "rhsType" simple)
                    aliases.Add(name,ident (get "longDotId" rhs),sourceRange info)
        if kind = "SynComponentInfo" then
            let n = ident (get "longId" f)
            if n <> "" then shadows.Add(n,sourceRange f)
    )
    // Associate locals with their enclosing lexical range rather than a file-wide name map.
    // Sibling functions and inner shadowing can no longer overwrite each other's aliases.
    for binding in bindingNodes do
        let _, f=fields (box binding)
        let pat=get "headPat" f
        let pk,pf=fields pat
        let rhs=get "expr" f
        let scope=scopes |> Seq.filter(fun r -> contains r binding.RangeOfBindingWithRhs) |> Seq.sortBy width |> Seq.head
        if pk="Named" then bindings.Add(ident(get "ident" pf),rhs,binding.RangeOfHeadPattern,scope)
        elif pk="LongIdent" then
            match rhs with
            | :? SynExpr as body ->
                walk 0 (get "argPats" pf) (fun p ->
                    let k,f=fields p
                    if k="Named" then bindings.Add(ident(get "ident" f),null,body.Range,body.Range)
                    elif k="Typed" then typedParameters.Add(p,body.Range))
            | _ -> ()
    for lambda in lambdaNodes do
        let _,lf=fields (box lambda)
        walk 0 (get "args" lf) (fun p ->
            let k,f=fields p
            if k="Id" then bindings.Add(ident(get "ident" f),null,lambda.Range,lambda.Range)
            elif k="Typed" then typedParameters.Add(p,lambda.Range))
    let declarationScope (declaration:range) = scopes |> Seq.filter(fun r -> contains r declaration) |> Seq.sortBy width |> Seq.head
    let inScope (at:range) (declaration:range) =
        contains (declarationScope declaration) at && (declaration.StartLine,declaration.StartColumn)<=(at.StartLine,at.StartColumn)
    let visible (at:range) name =
        bindings |> Seq.filter(fun (n,_,decl,scope) -> n=name && contains scope at && (decl.StartLine,decl.StartColumn)<=(at.StartLine,at.StartColumn))
                 |> Seq.sortBy(fun (_,_,decl,scope) -> width scope, -decl.StartLine, -decl.StartColumn) |> Seq.tryHead
    let typeOfParameter (at:range) name =
        typedParameters |> Seq.tryPick(fun (p,scope) ->
            let _,f=fields p
            let k,n=fields(get "pat" f)
            let _,typ=fields(get "targetType" f)
            if (k="Named" || k="Id") && ident(get "ident" n)=name && contains scope at then Some(ident(get "longDotId" typ),scope) else None)
    let rec canonicalAt depth (at:range) (name: string) =
        if depth > 12 || name = "" then "" else
        let head = name.Split('.')[0]
        let suffix = name.Substring(head.Length)
        let alias=aliases |> Seq.filter(fun (name,_,decl) -> name=head && inScope at decl)
                          |> Seq.sortBy(fun (_,_,decl) -> width(declarationScope decl),-decl.StartLine) |> Seq.tryHead
        match alias with
        | Some(_,target,_) -> canonicalAt (depth+1) at (target+suffix)
        | None ->
          match typeOfParameter at head, visible at head with
          | Some(typ,parameterScope),Some(_,_,_,localScope) when width localScope < width parameterScope -> ""
          | Some(typ,_),_ -> canonicalAt (depth+1) at (typ+suffix)
          | _,Some(_,rhs,decl,_) ->
            let target=exprName rhs
            if target="" || target=name then "" else
            let resolved=canonicalAt (depth+1) decl target
            let resolved=if resolved="System.Data.Common.DbConnection.CreateCommand" then "System.Data.Common.DbCommand" else resolved
            if resolved="" then "" else resolved+suffix
          | _ when shadows |> Seq.exists(fun (name,decl) -> name=head && inScope at decl) -> ""
          | _ when name.StartsWith("System.") -> name
          | _ ->
            let groups = ["System.Security.Cryptography", ["SHA1";"MD5";"DES";"TripleDES";"SHA1Managed";"MD5CryptoServiceProvider";"DESCryptoServiceProvider";"TripleDESCryptoServiceProvider"];
                          "System.Net", ["ServicePointManager"];
                          "System.Net.Http", ["HttpClientHandler"];
                          "System.Xml", ["DtdProcessing";"XmlReaderSettings"];
                          "System.Runtime.Serialization.Formatters.Binary", ["BinaryFormatter"];
                          "System.Diagnostics", ["Process"];
                          "System.Data.Common", ["DbCommand";"DbConnection"]]
            groups |> List.tryPick(fun (ns,names) -> if (opens |> Seq.exists(fun (name,decl) -> name=ns && inScope at decl)) && List.contains head names then Some(ns+"."+name) else None) |> Option.defaultValue ""
    let canonical (at:range) name = canonicalAt 0 at name
    let rec constructed depth (at:range) (value:obj) =
        if depth>10 || isNull value then false else
        let k,f=fields value
        if k="InterpolatedString" then true
        elif k="Paren" || k="Typed" then constructed (depth+1) at (get "expr" f)
        elif k="Ident" then
            match visible at (exprName value) with
            | Some(_,rhs,decl,_) -> constructed (depth+1) decl rhs
            | None -> false
        elif k="App" then
            exprName value="op_Addition" || (exprName value).EndsWith(".op_Addition")
        else false
    let rec stringValue (value:obj) =
        let k,f=fields value
        if k="Paren" then stringValue(get "expr" f)
        elif k="Const" then
            let ck,cf=fields(get "constant" f)
            if ck="String" then cf |> Map.toSeq |> Seq.tryPick(fun (_,v) -> match v with :? string as text -> Some text | _ -> None) else None
        else None
    let lines = code.Replace("\r\n","\n").Split('\n')
    let issues = List<Finding>()
    let add rule message severity (e: SynExpr) =
        if not (issues |> Seq.exists (fun i -> i.rule_id=rule && i.line=e.Range.StartLine)) then
            let evidence = if e.Range.StartLine > 0 && e.Range.StartLine <= lines.Length then lines[e.Range.StartLine-1] else ""
            issues.Add(Finding(rule,message,severity,e.Range.StartLine,evidence))
    let rec trueLambda (o: obj) =
        let k,f = fields o
        if k="Lambda" then
            let body = get "body" f
            let bk,bf = fields body
            if bk="Const" then
                let ck,cf = fields (get "constant" bf)
                ck="Bool" && (cf |> Map.toSeq |> Seq.exists (fun (_,v) -> v :? bool && unbox<bool> v))
            elif bk="Lambda" then trueLambda body
            else false
        elif k="Paren" then trueLambda (get "expr" f)
        else false
    for e in nodes do
        let k,f = fields (box e)
        if k="App" || k="New" then
            let name = canonical e.Range (exprName (box e))
            if name.StartsWith("System.Security.Cryptography.") && ([".MD5.";".SHA1.";".DES.";".TripleDES."] |> List.exists name.Contains) then
                add "dotnet.weak-crypto.v1" "A weak cryptographic primitive is used; replace security-sensitive uses with a modern algorithm." "medium" e
            if profile="security-v2" && name="System.Diagnostics.Process.Start" then
                let arg=get "argExpr" f
                let ak,af=fields arg
                let arg=if ak="Paren" then get "expr" af else arg
                let tk,tf=fields arg
                if tk="Tuple" then
                    let args=(get "exprs" tf :?> IEnumerable) |> Seq.cast<obj> |> Seq.toList
                    match args with
                    | executable::arguments::_ ->
                        match stringValue executable with
                        | Some shell when List.contains (shell.ToLowerInvariant()) ["sh";"bash";"cmd";"cmd.exe";"powershell";"powershell.exe"] && constructed 0 e.Range arguments ->
                            add "dotnet.shell-injection.v2" "Constructed arguments are passed to a shell interpreter; prefer a fixed executable and separate validated arguments." "high" e
                        | _ -> ()
                    | _ -> ()
            if name = "System.Runtime.Serialization.Formatters.Binary.BinaryFormatter.Deserialize" then
                add "dotnet.binary-formatter.v1" "BinaryFormatter deserialization is unsafe for untrusted input." "high" e
        if k="LongIdentSet" || k="DotSet" || k="Set" then
            let target =
                if k="LongIdentSet" then ident (get "longDotId" f)
                elif k="DotSet" then exprName (get "targetExpr" f) + "." + ident (get "longDotId" f)
                else exprName (get "targetExpr" f)
            let target = canonical e.Range target
            let rhs = if k="LongIdentSet" then get "expr" f else get "rhsExpr" f
            if profile="security-v2" && target="System.Data.Common.DbCommand.CommandText" && constructed 0 e.Range rhs then
                add "dotnet.sql-injection.v2" "Constructed SQL is assigned to a database command; use parameters for untrusted values." "high" e
            if (target="System.Net.ServicePointManager.ServerCertificateValidationCallback" || target="System.Net.Http.HttpClientHandler.ServerCertificateCustomValidationCallback") && trueLambda rhs then
                add "dotnet.tls-validation.v1" "Certificate validation callback always returns true." "high" e
            if target="System.Xml.XmlReaderSettings.DtdProcessing" && canonical e.Range (exprName rhs)="System.Xml.DtdProcessing.Parse" then
                add "dotnet.xml-dtd.v1" "DTD processing is explicitly enabled; prohibit DTDs for untrusted XML." "medium" e
    FileAnalysis(path,"fsharp",issues,errors)

[<EntryPoint>]
let main args =
    try
        if args = [|"--version"|] then
            printfn "codeagent-dotnet 1.1.0"
            0
        elif args.Length <> 1 then
            eprintfn "Usage: codeagent-dotnet <manifest.json>"
            2
        else
            let manifest = JsonDocument.Parse(File.ReadAllText(args[0]))
            let root = Path.GetFullPath(manifest.RootElement.GetProperty("workspace").GetString())
            let mutable profileElement=Unchecked.defaultof<JsonElement>
            let profile=if manifest.RootElement.TryGetProperty("profile",&profileElement) then profileElement.GetString() else "security-v1"
            if profile<>"security-v1" && profile<>"security-v2" then failwith "Unknown rule profile"
            let reports = ResizeArray<FileAnalysis>()
            for item in manifest.RootElement.GetProperty("files").EnumerateArray() do
                let rel = item.GetProperty("path").GetString()
                let lang = item.GetProperty("language").GetString()
                let full = Path.GetFullPath(Path.Combine(root,rel))
                if not (full.StartsWith(root + string Path.DirectorySeparatorChar, StringComparison.Ordinal)) then
                    failwith "File is outside the workspace"
                let code = File.ReadAllText(full)
                reports.Add(if lang="fsharp" then fsharpScan rel code profile else Analyzer.Scan(rel,code,lang,profile))
            printfn "%s" (JsonSerializer.Serialize(reports))
            0
    with ex ->
        eprintfn "%s" ex.Message
        2
