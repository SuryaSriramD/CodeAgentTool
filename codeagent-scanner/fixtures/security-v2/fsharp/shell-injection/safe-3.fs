module Sample
open System.Data.Common
open System.Diagnostics
let handle (db:DbConnection) (input:string) =
    printfn "%s" ("sh -c " + input)
