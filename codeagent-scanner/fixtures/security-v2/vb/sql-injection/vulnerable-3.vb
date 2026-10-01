Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
Dim command=db.CreateCommand()
Dim sql="SELECT * FROM users ORDER BY " & input
command.CommandText=sql
End Sub
End Module
