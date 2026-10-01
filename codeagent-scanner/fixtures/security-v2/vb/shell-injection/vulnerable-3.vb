Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
Dim command="-c " & input
Process.Start("bash",command)
End Sub
End Module
