cat << 'EOF'
  ______    ____  ____        _        _______      ______     ________   ______    
.' ____ \  |_   ||   _|      / \      |_   __ \    |_   _ `.  |_   __  | |_   _ `.  
| (___ \_|   | |__| |       / _ \       | |__) |     | | `. \   | |_ \_|   | | `. \ 
 _.____`.    |  __  |      / ___ \      |  __ /      | |  | |   |  _| _    | |  | | 
| \____) |  _| |  | |_   _/ /   \ \_   _| |  \ \_   _| |_.' /  _| |__/ |  _| |_.' / 
 \______.' |____||____| |____| |____| |____| |___| |______.'  |________| |______.'                                                                                  
EOF

echo "Welcome to Sharded!"
echo "This script will guide you through the setup process on required environment variables and configurations. Not every option will be presented here, please refer to the documentation at docs.sharded.app for more information."

read -p "Please enter your token: " TOKEN
echo

# Create or overwrite the .env file with the token
echo "TOKEN=$TOKEN" > .env

echo "Required configuration complete"
# Pull the Docker image

docker pull ghcr.io/shardedinteractive/sharded:latest

echo "Docker image has been pulled! Learn more on configuring at docs.sharded.app | Completing setup... (Service will automatically start in 10 seconds)"
sleep 10

docker run -d --env-file .env ghcr.io/shardedinteractive/sharded:latest
