using System.Data.Common;
using System.Diagnostics;
class Sample { void Handle(DbConnection db, string input) { var query="SELECT * FROM users WHERE name="+input; System.Console.WriteLine(query); } }
