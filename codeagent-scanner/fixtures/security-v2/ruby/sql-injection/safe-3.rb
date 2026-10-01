def handle(params)
User.find_by_sql(["SELECT * FROM users WHERE id=?", params[:id]])
end
