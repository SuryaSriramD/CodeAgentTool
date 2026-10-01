def handle(params)
User.where("id=" + params[:id])
end
