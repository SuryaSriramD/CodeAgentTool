import java.sql.Statement
import javax.xml.parsers.DocumentBuilderFactory
object Example { def handle(stmt: Statement, input: String, factory: DocumentBuilderFactory): Unit = {
stmt.execute("SELECT * FROM users ORDER BY " + input)
} }
