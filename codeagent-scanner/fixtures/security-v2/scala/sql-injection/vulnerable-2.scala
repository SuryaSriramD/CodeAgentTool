import java.sql.Statement
import javax.xml.parsers.DocumentBuilderFactory
object Example { def handle(stmt: Statement, input: String, factory: DocumentBuilderFactory): Unit = {
stmt.executeUpdate("DELETE FROM users WHERE id=" + input)
} }
