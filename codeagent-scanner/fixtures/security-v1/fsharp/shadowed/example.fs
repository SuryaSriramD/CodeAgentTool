module Example
open System.Security.Cryptography
open System.Net
open System.Xml
open System.Runtime.Serialization.Formatters.Binary
type MD5 =
    static member Create() = obj()
type BinaryFormatter() =
    member _.Deserialize(input:obj) = input
type ServicePointManager =
    static member val ServerCertificateValidationCallback = Unchecked.defaultof<System.Net.Security.RemoteCertificateValidationCallback> with get,set
type DtdProcessing = Parse | Prohibit
type XmlReaderSettings() =
    member val DtdProcessing = Prohibit with get,set
let value = MD5.Create()
let formatter = BinaryFormatter()
formatter.Deserialize(obj()) |> ignore
ServicePointManager.ServerCertificateValidationCallback <- fun _ _ _ _ -> true
let settings = XmlReaderSettings()
settings.DtdProcessing <- DtdProcessing.Parse
