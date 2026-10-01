using System.Net;
using System.Security.Cryptography;
using System.Runtime.Serialization.Formatters.Binary;
using System.Xml;
class Example { void Run(System.IO.Stream input) {
var hash = MD5.Create();
var formatter = new BinaryFormatter();
formatter.Deserialize(input);
ServicePointManager.ServerCertificateValidationCallback = (a,b,c,d) => true;
var settings = new XmlReaderSettings();
settings.DtdProcessing = DtdProcessing.Parse;
} }
