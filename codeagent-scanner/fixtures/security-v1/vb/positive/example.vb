Imports System.Net
Imports System.Security.Cryptography
Imports System.Runtime.Serialization.Formatters.Binary
Imports System.Xml
Public Class Example
Public Sub Run(input As System.IO.Stream)
Dim hash = MD5.Create()
Dim formatter As New BinaryFormatter()
formatter.Deserialize(input)
ServicePointManager.ServerCertificateValidationCallback = Function(a,b,c,d) True
Dim settings As New XmlReaderSettings()
settings.DtdProcessing = DtdProcessing.Parse
End Sub
End Class
