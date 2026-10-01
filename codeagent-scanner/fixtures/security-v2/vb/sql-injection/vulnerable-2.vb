Imports System.Data.Common
Imports System.Diagnostics
Module Sample
Sub Handle(db As DbConnection, input As String)
Dim cmd As DbCommand = db.CreateCommand()
cmd.CommandText=$"DELETE FROM users WHERE id={input}"
End Sub
End Module
