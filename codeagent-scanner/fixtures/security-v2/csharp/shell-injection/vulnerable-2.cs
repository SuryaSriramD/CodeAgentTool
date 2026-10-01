using System.Data.Common;
using System.Diagnostics;
class Sample { void Handle(DbConnection db, string input) { System.Diagnostics.Process.Start("cmd.exe", "/c "+input); } }
