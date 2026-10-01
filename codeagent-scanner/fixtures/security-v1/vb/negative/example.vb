Imports System.Net
Imports System.Security.Cryptography
Imports System.Runtime.Serialization.Formatters.Binary
Imports System.Xml
Public Class Example
Public Sub Run(input As System.IO.Stream)
Dim hash = SHA256.Create()
Dim formatter As New BinaryFormatter()
System.Text.Json.JsonSerializer.Deserialize(Of Object)(input)
ServicePointManager.ServerCertificateValidationCallback = Function(a,b,c,d) False
Dim settings As New XmlReaderSettings()
settings.DtdProcessing = DtdProcessing.Prohibit
End Sub
End Class
