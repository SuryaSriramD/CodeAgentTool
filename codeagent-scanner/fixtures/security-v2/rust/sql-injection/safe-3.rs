fn handle(input: &str, connection: rusqlite::Connection) {
connection.prepare("SELECT * FROM users WHERE name=?1");
}
