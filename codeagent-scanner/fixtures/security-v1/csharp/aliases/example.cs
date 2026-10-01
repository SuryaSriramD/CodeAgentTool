using Weak = System.Security.Cryptography.MD5;
using Formatter = System.Runtime.Serialization.Formatters.Binary.BinaryFormatter;
using Network = System.Net.ServicePointManager;
using Settings = System.Xml.XmlReaderSettings;
using Dtd = System.Xml.DtdProcessing;
using System.Net;
using System.Security.Cryptography;
using System.Runtime.Serialization.Formatters.Binary;
using System.Xml;
class Example { void Run(System.IO.Stream input) {
var hash = Weak.Create();
var formatter = new Formatter();
formatter.Deserialize(input);
Network.ServerCertificateValidationCallback = (a,b,c,d) => true;
var settings = new Settings();
settings.DtdProcessing = Dtd.Parse;
} }
