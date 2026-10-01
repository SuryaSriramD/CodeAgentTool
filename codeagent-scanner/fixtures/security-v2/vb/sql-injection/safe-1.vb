Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
Dim cmd=db.CreateCommand()
cmd.CommandText="SELECT * FROM users WHERE name=@name"
End Sub
End Module
