module Sample
open System.Data.Common
open System.Diagnostics
let handle (db:DbConnection) (input:string) =
    let cmd = db.CreateCommand()
    let sql = "SELECT * FROM users ORDER BY " + input
    cmd.CommandText <- sql
