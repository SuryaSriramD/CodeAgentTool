def handle(params)
User.where("name = '#{params[:name]}'")
end
