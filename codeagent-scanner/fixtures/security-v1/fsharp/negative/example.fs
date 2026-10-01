module Example
open System.Net
open System.Xml
open System.Security.Cryptography
open System.Runtime.Serialization.Formatters.Binary
let hash = SHA256.Create()
let formatter = new BinaryFormatter()
let deserialize stream = System.Text.Json.JsonSerializer.Deserialize<obj>(stream)
ServicePointManager.ServerCertificateValidationCallback <- fun _ _ _ _ -> false
let settings = XmlReaderSettings()
settings.DtdProcessing <- DtdProcessing.Prohibit
