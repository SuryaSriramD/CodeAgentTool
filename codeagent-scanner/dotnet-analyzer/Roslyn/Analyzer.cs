using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.VisualBasic;
using System.Text.Json.Serialization;

namespace CodeAgent.DotNet;

public sealed record Finding(string rule_id, string message, string severity, int line, string evidence) {
    public int end_line { get; init; } = line;
    public string family => rule_id.Split('.')[1];
    public string cwe => family switch { "sql-injection"=>"CWE-89", "shell-injection"=>"CWE-78", "weak-crypto"=>"CWE-327", "binary-formatter"=>"CWE-502", "tls-validation"=>"CWE-295", "xml-dtd"=>"CWE-611", _=>"" };
}
public sealed record FileAnalysis(string path, string language, List<Finding> issues, List<string> errors);

public static class Analyzer
{
    private static readonly string[] TrustedNamespaces = { "System.Security.Cryptography", "System.Net", "System.Net.Http", "System.Xml", "System.Runtime.Serialization.Formatters.Binary" };
    public static FileAnalysis Scan(string path, string code, string language, string profile = "security-v1")
    {
        var tree = language == "vb"
            ? (SyntaxTree)VisualBasicSyntaxTree.ParseText(code, path: path)
            : CSharpSyntaxTree.ParseText(code, path: path);
        var errors = tree.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error).Select(d => d.ToString()).ToList();
        // Only metadata installed with this analyzer is referenced. No MSBuild, restore,
        // repository assemblies, source generators, Emit, or application execution.
        var refs = ((string?)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES") ?? "")
            .Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries)
            .Where(p => Path.GetFileName(p).StartsWith("System.") || Path.GetFileName(p) is "mscorlib.dll" or "netstandard.dll" or "Microsoft.VisualBasic.Core.dll")
            .Select(p => MetadataReference.CreateFromFile(p)).ToArray();
        Compilation compilation = language == "vb"
            ? VisualBasicCompilation.Create("SourceReview", new[] { tree }, refs,
                new VisualBasicCompilationOptions(OutputKind.DynamicallyLinkedLibrary))
            : CSharpCompilation.Create("SourceReview", new[] { tree }, refs,
                new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
        var model = compilation.GetSemanticModel(tree);
        var issues = new List<Finding>();
        void Add(string id, string message, string severity, SyntaxNode node)
        {
            var line = tree.GetLineSpan(node.Span).StartLinePosition.Line + 1;
            if (!issues.Any(x => x.rule_id == id && x.line == line))
                issues.Add(new(id, message, severity, line, node.ToString()) { end_line=tree.GetLineSpan(node.Span).EndLinePosition.Line+1 });
        }
        string Qualified(SyntaxNode node)
        {
            var symbol = model.GetSymbolInfo(node).Symbol;
            if (symbol == null) return "";
            if (symbol.ContainingType != null)
                return symbol.ContainingType.ToDisplayString() + "." + symbol.Name;
            return symbol.ToDisplayString();
        }
        bool Constructed(SyntaxNode expression, int depth = 0) {
            if (depth > 8 || model.GetConstantValue(expression).HasValue) return false;
            if (expression is Microsoft.CodeAnalysis.CSharp.Syntax.InterpolatedStringExpressionSyntax ci)
                return ci.Contents.OfType<Microsoft.CodeAnalysis.CSharp.Syntax.InterpolationSyntax>().Any();
            if (expression is Microsoft.CodeAnalysis.VisualBasic.Syntax.InterpolatedStringExpressionSyntax vi)
                return vi.Contents.OfType<Microsoft.CodeAnalysis.VisualBasic.Syntax.InterpolationSyntax>().Any();
            if (expression is Microsoft.CodeAnalysis.CSharp.Syntax.BinaryExpressionSyntax cb && cb.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.AddExpression)) return true;
            if (expression is Microsoft.CodeAnalysis.VisualBasic.Syntax.BinaryExpressionSyntax vb &&
                (vb.IsKind(Microsoft.CodeAnalysis.VisualBasic.SyntaxKind.ConcatenateExpression) || vb.IsKind(Microsoft.CodeAnalysis.VisualBasic.SyntaxKind.AddExpression))) return true;
            var symbol=model.GetSymbolInfo(expression).Symbol;
            if (symbol is ILocalSymbol local) {
                foreach (var reference in local.DeclaringSyntaxReferences) {
                    var declaration=reference.GetSyntax();
                    if (declaration is Microsoft.CodeAnalysis.CSharp.Syntax.VariableDeclaratorSyntax cv && cv.Initializer!=null)
                        return Constructed(cv.Initializer.Value, depth+1);
                    var vv=declaration.AncestorsAndSelf().OfType<Microsoft.CodeAnalysis.VisualBasic.Syntax.VariableDeclaratorSyntax>().FirstOrDefault();
                    if (vv?.Initializer!=null) return Constructed(vv.Initializer.Value, depth+1);
                }
            }
            return false;
        }
        foreach (var node in tree.GetRoot().DescendantNodes())
        {
            bool invocation = node is Microsoft.CodeAnalysis.CSharp.Syntax.InvocationExpressionSyntax
                || node is Microsoft.CodeAnalysis.VisualBasic.Syntax.InvocationExpressionSyntax;
            bool creation = node is Microsoft.CodeAnalysis.CSharp.Syntax.ObjectCreationExpressionSyntax
                || node is Microsoft.CodeAnalysis.VisualBasic.Syntax.ObjectCreationExpressionSyntax;
            var name = invocation || creation ? Qualified(node) : "";
            if (name.StartsWith("System.Security.Cryptography.", StringComparison.Ordinal) &&
                new[] { ".MD5.", ".SHA1.", ".DES.", ".TripleDES.", ".MD5CryptoServiceProvider.", ".SHA1Managed.", ".DESCryptoServiceProvider.", ".TripleDESCryptoServiceProvider." }.Any(name.Contains))
                Add("dotnet.weak-crypto.v1", "A weak cryptographic primitive is used; replace security-sensitive uses with a modern algorithm.", "medium", node);
            if (name.StartsWith("System.Runtime.Serialization.Formatters.Binary.BinaryFormatter.", StringComparison.Ordinal)
                && name.Contains("Deserialize"))
                Add("dotnet.binary-formatter.v1", "BinaryFormatter deserialization is unsafe for untrusted input.", "high", node);

            if (profile=="security-v2" && invocation && name=="System.Diagnostics.Process.Start") {
                var args=node is Microsoft.CodeAnalysis.CSharp.Syntax.InvocationExpressionSyntax call
                    ? call.ArgumentList.Arguments.Select(a=>(SyntaxNode)a.Expression).ToArray()
                    : ((Microsoft.CodeAnalysis.VisualBasic.Syntax.InvocationExpressionSyntax)node).ArgumentList.Arguments
                        .OfType<Microsoft.CodeAnalysis.VisualBasic.Syntax.SimpleArgumentSyntax>().Select(a=>(SyntaxNode)a.Expression).ToArray();
                if (args.Length >= 2 && model.GetConstantValue(args[0]).Value is string executable &&
                    new[]{"sh","bash","cmd","cmd.exe","powershell","powershell.exe"}.Contains(executable.ToLowerInvariant()) && Constructed(args[1]))
                    Add("dotnet.shell-injection.v2","Constructed arguments are passed to a shell interpreter; use a fixed executable and separate validated arguments.","high",node);
            }
            SyntaxNode? left = null, right = null;
            if (node is Microsoft.CodeAnalysis.CSharp.Syntax.AssignmentExpressionSyntax ca) { left = ca.Left; right = ca.Right; }
            if (node is Microsoft.CodeAnalysis.VisualBasic.Syntax.AssignmentStatementSyntax va) { left = va.Left; right = va.Right; }
            if (node is Microsoft.CodeAnalysis.CSharp.Syntax.EqualsValueClauseSyntax ce && ce.Parent is Microsoft.CodeAnalysis.CSharp.Syntax.VariableDeclaratorSyntax)
                continue;
            if (left != null && right != null)
            {
                var target = Qualified(left);
                if (profile=="security-v2" && target=="System.Data.Common.DbCommand.CommandText" && Constructed(right))
                    Add("dotnet.sql-injection.v2","Constructed SQL is assigned to a database command; use parameters for untrusted values.","high",node);
                if ((target == "System.Net.ServicePointManager.ServerCertificateValidationCallback" ||
                     target == "System.Net.Http.HttpClientHandler.ServerCertificateCustomValidationCallback") &&
                    AlwaysTrue(right, model))
                    Add("dotnet.tls-validation.v1", "Certificate validation callback always returns true.", "high", node);
                if (target == "System.Xml.XmlReaderSettings.DtdProcessing" &&
                    Qualified(right) == "System.Xml.DtdProcessing.Parse")
                    Add("dotnet.xml-dtd.v1", "DTD processing is explicitly enabled; prohibit DTDs for untrusted XML.", "medium", node);
            }
            // Object initializer properties are distinct VB nodes, unlike C# assignments.
            if (node is Microsoft.CodeAnalysis.VisualBasic.Syntax.NamedFieldInitializerSyntax init)
            {
                var target = Qualified(init.Name);
                if (target == "System.Xml.XmlReaderSettings.DtdProcessing" && Qualified(init.Expression) == "System.Xml.DtdProcessing.Parse")
                    Add("dotnet.xml-dtd.v1", "DTD processing is explicitly enabled; prohibit DTDs for untrusted XML.", "medium", node);
            }
        }
        return new(path, language, issues, errors);
    }

    private static bool AlwaysTrue(SyntaxNode node, SemanticModel model)
    {
        if (node is Microsoft.CodeAnalysis.CSharp.Syntax.ParenthesizedLambdaExpressionSyntax p)
            return BodyTrue(p.Body, model);
        if (node is Microsoft.CodeAnalysis.CSharp.Syntax.SimpleLambdaExpressionSyntax s)
            return BodyTrue(s.Body, model);
        if (node is Microsoft.CodeAnalysis.VisualBasic.Syntax.SingleLineLambdaExpressionSyntax v)
            return BodyTrue(v.Body, model);
        if (node is Microsoft.CodeAnalysis.VisualBasic.Syntax.MultiLineLambdaExpressionSyntax m)
            return m.Statements.Count == 1 && m.Statements[0] is Microsoft.CodeAnalysis.VisualBasic.Syntax.ReturnStatementSyntax r && r.Expression != null && ConstantTrue(r.Expression, model);
        return false;
    }
    private static bool BodyTrue(SyntaxNode node, SemanticModel model)
    {
        if (ConstantTrue(node, model)) return true;
        return node is Microsoft.CodeAnalysis.CSharp.Syntax.BlockSyntax b && b.Statements.Count == 1 &&
            b.Statements[0] is Microsoft.CodeAnalysis.CSharp.Syntax.ReturnStatementSyntax r && r.Expression != null && ConstantTrue(r.Expression, model);
    }
    private static bool ConstantTrue(SyntaxNode node, SemanticModel model)
    {
        var value = model.GetConstantValue(node);
        return value.HasValue && value.Value is true;
    }
}
