def handle(params)
YAML.unsafe_load(params[:document])
end
