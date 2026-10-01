module Sample
open System.Data.Common
open System.Diagnostics
let handle (db:DbConnection) (input:string) =
    Process.Start("sh", "-c " + input) |> ignore
