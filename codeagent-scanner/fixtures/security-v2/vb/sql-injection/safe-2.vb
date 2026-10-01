Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
Dim cmd=db.CreateCommand()
cmd.CommandText="SELECT count(*) FROM users"
End Sub
End Module
