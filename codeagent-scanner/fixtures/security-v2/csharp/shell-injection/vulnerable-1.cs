using System.Data.Common;
using System.Diagnostics;
class Sample { void Handle(DbConnection db, string input) { Process.Start("sh", "-c "+input); } }
