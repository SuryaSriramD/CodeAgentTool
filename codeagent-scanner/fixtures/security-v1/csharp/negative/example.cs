using System.Net;
using System.Security.Cryptography;
using System.Runtime.Serialization.Formatters.Binary;
using System.Xml;
class Example { void Run(System.IO.Stream input) {
var hash = SHA256.Create();
var formatter = new BinaryFormatter();
System.Text.Json.JsonSerializer.Deserialize<object>(input);
ServicePointManager.ServerCertificateValidationCallback = (a,b,c,d) => false;
var settings = new XmlReaderSettings();
settings.DtdProcessing = DtdProcessing.Prohibit;
} }
