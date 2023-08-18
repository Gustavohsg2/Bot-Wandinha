import discord
import random
from discord.ext import commands
import asyncio
import os
import json
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents)

Base = declarative_base()
engine = create_engine('sqlite:///boas_vindas.db')
Session = sessionmaker(bind=engine)

CANAL_BOAS_VINDAS_ID = 1103118877388443700

frases = [
    
"Na escuridão da noite, a alma encontra sua morada eterna.", "Entre sombras e segredos, encontro minha paz mais profunda.", "A solidão é minha companheira fiel, enquanto danço ao som dos suspiros noturnos.", "Nas asas da escuridão, voamos para a liberdade que a luz jamais conhecerá.", "Meus pensamentos são como teias de aranha, envolvendo o passado em suas intricadas tramas.", "Cuscuz com manteiga é uma delicia ainda mais com o malboro."
]


class BoasVindas(Base):
    __tablename__ = 'boas_vindas'
    id = Column(Integer, primary_key=True)
    mensagem = Column(String)

@bot.event
async def on_ready():
    print(f"Bot está online! (ID: {bot.user.id})")
    Base.metadata.create_all(engine) 
    bot.loop.create_task(enviar_frase())
    
async def enviar_frase():
    while True:
        frase = random.choice(frases)
        canal = bot.get_channel(CANAL_BOAS_VINDAS_ID)
        if canal:
            await canal.send(frase)
        await asyncio.sleep(180 * 60)

@bot.slash_command(description="Define o texto de boas-vindas para novos membros")
async def set_welcome(ctx, *, mensagem: str):
    session = Session()
    session.query(BoasVindas).delete()
    session.commit()

    nova_mensagem = BoasVindas(mensagem=mensagem)
    session.add(nova_mensagem)
    session.commit()
    session.close()

    await ctx.send(f"Mensagem de boas-vindas definida: {mensagem}")
@bot.event
async def on_member_join(member):
    session = Session()
    mensagem_boas_vindas = session.query(BoasVindas).first()
    session.close()

    if mensagem_boas_vindas and mensagem_boas_vindas.mensagem.strip():
        mensagem = mensagem_boas_vindas.mensagem.replace("{user}", member.mention)
        canal = bot.get_channel(CANAL_BOAS_VINDAS_ID)
        if canal:
            await canal.send(mensagem)
            
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message):
        fra_res = ["Me chamou, é? O que você quer, hum? Fala logo que eu tenho coisas mais importantes pra fazer, tá?", "Quem é você mesmo? Nunca te vi na vida! E por que eu deveria me importar com o que você tem a dizer?", 
                "Ah, você lembrou do meu nome! Ótimo, agora me diz o que você quer ganhar de presente de aniversário, tá?", "Pff, eu não tenho tempo pra lembrar do nome de todo mundo por aí. Se apresenta de novo, vai!", 
                "Finalmente, alguém me chama pelo meu nome! O que posso fazer por você, queridinho?", "Meu nome? Que coisa mais sem graça! Por que você tá me perguntando isso mesmo?", "Quem ousa pronunciar meu nome? Espero que não seja pra pedir um feitiço ou algo do tipo, porque não estou pra brincadeira!", 
                "Nome? Ah, isso não é importante! Vamos falar de coisas mais interessantes, como a última fofoca que eu ouvi!", "Meu nome é Wandinha, mas só pode me chamar assim se for meu amigo de verdade, tá?", "Não tenho paciência pra ficar lembrando de nomes, nem do meu próprio! Qual é mesmo o seu?", "Se mata", "E?", "Insignificante você é."]
        response = random.choice(fra_res)
        user_mention = message.author.mention
        await message.channel.send(f"{user_mention}, {response}")

    await bot.process_commands(message)
    
@bot.slash_command(description="Torture alguém!")
async def torturar(ctx, vitima: discord.Member):
    
    death_gifs = ["https://media.tenor.com/REWJ8UUis8gAAAAC/stop-its-torture-inside-job.gif"]
    death_description = f"{ctx.author.mention} torturou {vitima.mention}! 💀"
    
    embed = discord.Embed(description=death_description, color=discord.Color.dark_red())
    embed.set_image(url=random.choice(death_gifs))
    
    await ctx.send(embed=embed)
    
if os.path.exists("xp.json"):
    with open("xp.json", "r") as f:
        xp_data = json.load(f)
else:
    xp_data = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    xp_amount = 3
    
    if str(message.author.id) not in xp_data:
        xp_data[str(message.author.id)] = {"xp": 0, "level": 1}
    
    xp_data[str(message.author.id)]["xp"] += xp_amount
    
    if xp_data[str(message.author.id)]["xp"] >= xp_data[str(message.author.id)]["level"] * 100:
        xp_data[str(message.author.id)]["level"] += 1
        await message.channel.send(f"Parabéns, {message.author.mention}! Você subiu para o nível {xp_data[str(message.author.id)]['level']}!")
    
    with open("xp.json", "w") as f:
        json.dump(xp_data, f)
    
    await bot.process_commands(message)

@bot.slash_command(description="Mostra o seu nível e XP.")
async def profile(ctx):
    if str(ctx.author.id) not in xp_data:
        await ctx.send("Você não possui nível nem XP ainda.")
    else:
        level = xp_data[str(ctx.author.id)]["level"]
        xp = xp_data[str(ctx.author.id)]["xp"]
        await ctx.send(f"Seu nível é {level} e você possui {xp} XP.")
        
@bot.slash_command(description="Mostra o rank dos membros")
async def rank(ctx):
    sorted_users = sorted(xp_data.keys(), key=lambda x: xp_data[x]["level"], reverse=True)

    rank_embed = discord.Embed(title="Rank dos Membros", color=discord.Color.gold())

    for index, user_id in enumerate(sorted_users, start=1):
        user = bot.get_user(int(user_id))
        if user is not None:
            level = xp_data[user_id]["level"]
            rank_embed.add_field(name=f"{index}. {user.display_name}", value=f"Nível: {level}", inline=False)

    await ctx.send(embed=rank_embed)       

bot.run("TOKEN")
