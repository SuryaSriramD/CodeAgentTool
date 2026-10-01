Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
Process.Start("sh","-c uptime")
End Sub
End Module
