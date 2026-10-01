Imports Weak = System.Security.Cryptography.MD5
Imports Formatter = System.Runtime.Serialization.Formatters.Binary.BinaryFormatter
Imports Network = System.Net.ServicePointManager
Imports Settings = System.Xml.XmlReaderSettings
Imports Dtd = System.Xml.DtdProcessing
Imports System.Net
Imports System.Security.Cryptography
Imports System.Runtime.Serialization.Formatters.Binary
Imports System.Xml
Public Class Example
Public Sub Run(input As System.IO.Stream)
Dim hash = Weak.Create()
Dim formatter As New Formatter()
formatter.Deserialize(input)
Network.ServerCertificateValidationCallback = Function(a,b,c,d) True
Dim settings As New Settings()
settings.DtdProcessing = Dtd.Parse
End Sub
End Class
