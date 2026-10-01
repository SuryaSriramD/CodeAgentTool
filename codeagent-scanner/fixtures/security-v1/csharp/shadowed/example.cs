using System.Security.Cryptography;
class MD5 { public static object Create() => new object(); }
class BinaryFormatter { public object Deserialize(object input) => input; }
class ServicePointManager { public static System.Net.Security.RemoteCertificateValidationCallback ServerCertificateValidationCallback {get;set;} }
enum DtdProcessing { Parse, Prohibit }
class XmlReaderSettings { public DtdProcessing DtdProcessing {get;set;} }
class Example { void Run(object input) {
var value = MD5.Create();
new BinaryFormatter().Deserialize(input);
ServicePointManager.ServerCertificateValidationCallback = (a,b,c,d) => true;
new XmlReaderSettings().DtdProcessing = DtdProcessing.Parse;
} }
