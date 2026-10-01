module Sample
open System.Data.Common
open System.Diagnostics
let handle (db:DbConnection) (input:string) =
    let cmd = db.CreateCommand()
    cmd.CommandText <- $"DELETE FROM users WHERE id={input}"
