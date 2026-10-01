fn handle(input: &str, connection: rusqlite::Connection) {
connection.execute("DELETE FROM users WHERE id=?1", [input]);
}
