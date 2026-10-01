module Sample
open System.Data.Common
open System.Diagnostics
let handle (db:DbConnection) (input:string) =
    System.Diagnostics.Process.Start("cmd.exe", "/c " + input) |> ignore
