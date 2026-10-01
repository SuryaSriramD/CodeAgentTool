fn handle(input: &str, connection: rusqlite::Connection) {
sqlx::query("SELECT * FROM users WHERE name=$1").bind(input);
}
