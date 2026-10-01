using System.Data.Common;
using System.Diagnostics;
class Sample { void Handle(DbConnection db, string input) { System.Console.WriteLine("sh -c "+input); } }
