import requests

request = input("1 -> get \n2 -> post\n -> ")

if request == "1":
  url = input("URL do Load Balancer -> ")
  response = requests.get(url)
  print(response)
  print(response.json())

elif request == "2":
  url = input("URL do Load Balancer -> ")
  title = input("título -> ")
  anomesdia = input("(YYYY)-(MM)-(DD) -> ")
  hora = input("(hh):(mm) -> ")
  date = f"{anomesdia}T{hora}"
  description = input("descrição: ")

  response = requests.post(
    url, 
    data={
      "title": title,
      "pub_date": date,
      "description": description
    }
  )
  print(response)
  print(response.json())

else: 
    print("input inválido")