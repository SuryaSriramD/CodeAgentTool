module Sample
open System.Data.Common
open System.Diagnostics
let handle (db:DbConnection) (input:string) =
    let sql="SELECT * FROM users WHERE name=" + input
    printfn "%s" sql
