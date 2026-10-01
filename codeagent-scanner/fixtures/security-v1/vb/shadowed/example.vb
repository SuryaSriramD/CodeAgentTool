Imports System.Security.Cryptography
Public Class MD5
Public Shared Function Create() As Object
Return New Object()
End Function
End Class
Public Class BinaryFormatter
Public Function Deserialize(input As Object) As Object
Return input
End Function
End Class
Public Class ServicePointManager
Public Shared Property ServerCertificateValidationCallback As System.Net.Security.RemoteCertificateValidationCallback
End Class
Public Enum DtdProcessing
Parse
Prohibit
End Enum
Public Class XmlReaderSettings
Public Property DtdProcessing As DtdProcessing
End Class
Public Class Example
Public Sub Run(input As Object)
Dim value = MD5.Create()
Dim formatter As New BinaryFormatter()
formatter.Deserialize(input)
ServicePointManager.ServerCertificateValidationCallback = Function(a,b,c,d) True
Dim settings As New XmlReaderSettings()
settings.DtdProcessing = DtdProcessing.Parse
End Sub
End Class
