module Example
open System.Net
open System.Xml
open System.Security.Cryptography
open System.Runtime.Serialization.Formatters.Binary
let hash = MD5.Create()
let formatter = new BinaryFormatter()
let deserialize stream = formatter.Deserialize(stream)
ServicePointManager.ServerCertificateValidationCallback <- fun _ _ _ _ -> true
let settings = XmlReaderSettings()
settings.DtdProcessing <- DtdProcessing.Parse
