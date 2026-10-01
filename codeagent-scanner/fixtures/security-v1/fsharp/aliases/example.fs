module Example
open System.Net
open System.Xml
open System.Security.Cryptography
open System.Runtime.Serialization.Formatters.Binary
type Weak = System.Security.Cryptography.MD5
type Formatter = System.Runtime.Serialization.Formatters.Binary.BinaryFormatter
type Network = System.Net.ServicePointManager
type Settings = System.Xml.XmlReaderSettings
type Dtd = System.Xml.DtdProcessing
let hash = Weak.Create()
let formatter = new Formatter()
let deserialize stream = formatter.Deserialize(stream)
Network.ServerCertificateValidationCallback <- fun _ _ _ _ -> true
let settings = Settings()
settings.DtdProcessing <- Dtd.Parse
