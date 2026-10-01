module Sample
open System.Data.Common
open System.Diagnostics
let handle (db:DbConnection) (input:string) =
    let cmd = db.CreateCommand()
    cmd.CommandText <- "SELECT * FROM users WHERE name=@name"
