module Sample
open System.Data.Common
open System.Diagnostics
let handle (db:DbConnection) (input:string) =
    let command="-c " + input
    Process.Start("bash", command) |> ignore
