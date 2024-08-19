import json
import random
import asyncio
import discord
from discord.ext import commands

client = commands.Bot(command_prefix="$")
# client.remove_command('help')
mainshop = [
    {'name': 'MEGA_Roller', 'price': 100000, 'description': 'GET THE MEGA ROLLER ROLE TO FLEX'},
    {'name': 'High_Roller', 'price': 50000, 'description': 'Get a special role to flex on those none high rollers'},
    {'name': 'Watch', 'price': 100, 'description': 'A way to tell the time'},
    {'name': 'Doggo', 'price': 1000, 'description': '1.5 multiplier for begging because everyone loves doggos'},
    {'name': 'Lucky_Cat', 'price': 5000, 'description': '1.5 multiplier for slots because you have extra luck'}
]

player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]





@client.command()
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member, betting: int = 0):
    global count
    global player1
    global player2
    global turn
    global gameOver
    global pot

    if gameOver:
        if betting > 1000:
            await ctx.send('You cannot bet more than 1000 dollars')
            return
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        count = 0

        player1 = p1
        player2 = p2
        print(player2, player1)
        if str(ctx.author) == str(player1):
            await ctx.send(f'Please wait for {player2} to accept')
        else:
            player2 = ''
            player1 = ''
            await ctx.send('Please put you name first then whoever you want to verse')
        pot = betting
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")


@client.command()
async def accept(ctx):
    global count
    global player1
    global player2
    global turn
    global gameOver
    if gameOver:
        print(ctx.author, player2)
        if str(ctx.author) == str(player2):
            turn = ""
            gameOver = False
            count = 0

            # print the board
            line = ""
            for x in range(len(board)):
                if x == 2 or x == 5 or x == 8:
                    line += " " + board[x]
                    await ctx.send(line)
                    line = ""
                else:
                    line += " " + board[x]

            # determine who goes first
            num = random.randint(1, 2)
            if num == 1:
                turn = player1
                await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
            elif num == 2:
                turn = player2
                await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
        else:
            await ctx.send('you are not allowed')


@client.command()
async def sell(ctx, item, amount: int = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(f"You don't have {amount} {item} in your bag.")
            return
        if res[1] == 3:
            await ctx.send(f"You don't have {item} in your bag.")
            return

    await ctx.send(f"You just sold {amount} {item}.")


async def sell_this(user, item_name, amount, price=None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price == None:
                price = 0.9 * item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price * amount

    users = await get_user_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False, 2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            return [False, 3]
    except:
        return [False, 3]

    with open("users info.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost, "wallet")

    return [True, "Worked"]


@client.command()
async def place(ctx, pos: int):
    global turn
    global player
    global player2
    global board
    global count
    global gameOver
    global pot
    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
                board[pos - 1] = mark
                count += 1

                # print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)

                if gameOver:
                    await ctx.send(mark + " wins!")
                    await open_account(player1)
                    await open_account(player2)
                    if turn == player1:
                        await update_bank(player1, pot)
                        await update_bank(player2, pot * -1)
                    else:
                        await update_bank(player2, pot)
                        await update_bank(player1, pot * -1)
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a tie!")

                # switch turns
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the !tictactoe command.")


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True


@tictactoe.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players.")


@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an number.")


@client.event
async def on_ready():
    print('ready')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.message.delete()
        await ctx.send('You do not have permission')
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You are missing an argument.\nPlease enter all required arguments')
        return
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('That is not a valid command')
        return
    print(error)


@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name='DJ')
    await member.add_roles(role)


@client.command(aliases=['bal'])
async def balance(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    await open_account(member)

    users = await get_user_data()
    wallet_bal = users[str(member.id)]['wallet']
    bank_bal = users[str(member.id)]['bank']
    mess = users[str(member.id)]['messages sent']

    em = discord.Embed(title=f'{member.name}\'s balance')
    em.add_field(name='Wallet balance', value=wallet_bal)
    em.add_field(name='Bank balance', value=bank_bal)
    em.add_field(name='mes', value=mess)
    await ctx.send(embed=em)




@client.command(aliases=["lb"])
async def leaderboard(ctx, x=1):
    users = await get_user_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(title=f"Top {x} Richest People",
                       description="This is decided on the basis of raw money in the bank and wallet",
                       color=discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await client.fetch_user(id_)
        name = member.name
        em.add_field(name=f"{index}. {name}", value=f"{amt}")
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed=em)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if str(message.author) == 'Rythm#3722':
        return
    await new_mes(message.author)


def get_quote():
    quote_list = get_lines()
    quote = quote_list[random.randint(0, len(quote_list) - 1)]
    return quote


async def open_account(user):
    with open('users info.json', 'r') as f:
        users = json.load(f)

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]['wallet'] = 0
        users[str(user.id)]['bank'] = 0
        users[str(user.id)]['messages sent'] = 0
    with open('users info.json', 'w') as f:
        json.dump(users, f)
    return True


def get_lines():
    # get all the usernames from the docs
    list_in_txt = []
    file = open('henesy quotes', 'r')
    for lines in file:
        list_in_txt.append(f'{lines.strip()}')
    file.close()
    return list_in_txt


def add_quote(msg):
    file = open('henesy quotes', 'a')
    file.write(f'\n{msg.strip()}')
    file.close()


async def get_user_data():
    with open('users info.json', 'r') as f:
        users = json.load(f)
    return users


@client.command(aliases=['add-hen-quote'])
async def ahq(ctx, msg):
    add_quote(msg)
    await ctx.send('Thank you for the quote')


@client.command()
async def hen(ctx):
    await ctx.send(get_quote() + '- Mr Hennessy')


@client.command()
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_user_data()
    bag = await open_bag(ctx.author)
    if random.randint(0, 2) == 1:

        earnings = random.randrange(101)
    else:
        earnings = random.randrange(31)
    doggo = False
    for item in bag:
        if item['item'] == 'doggo':
            earnings = int(earnings * 1.5)
            await ctx.send(f'And your dog boosted you!!!\nYou got {earnings} dollars')
            doggo = True
            break
    users[str(ctx.author.id)]['wallet'] += earnings
    if doggo is False:
        await ctx.send(f'Someone gave {earnings} dollars')
    with open('users info.json', 'w') as f:
        json.dump(users, f)


async def new_mes(user):
    await open_account(user)

    users = await get_user_data()
    users[str(user.id)]['messages sent'] += 1
    with open('users info.json', 'w') as f:
        json.dump(users, f)


async def update_bank(user, change=0, mode='wallet'):
    users = await get_user_data()

    users[str(user.id)][mode] += change

    with open('users info.json', 'w') as f:
        json.dump(users, f)
    bal = [users[str(user.id)]['wallet'], users[str(user.id)]['bank']]
    return bal


@client.command(aliases=['with'])
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)
    if amount is None:
        await ctx.send('I need amount to withdraw')
    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[1]
    else:
        try:
            amount = int(amount)
        except:
            await ctx.send('please put a number or all')
            return
        if amount > bal[1]:
            await ctx.send('You don\'t have that much money!')
            return
        if amount < 0:
            await ctx.send('Amount must be positive!')
            return
    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1 * amount, 'bank')
    await ctx.send(f'You withdrew {amount} dollars')


@client.command(aliases=['dep'])
async def deposit(ctx, amount=None):
    await open_account(ctx.author)
    if amount is None:
        await ctx.send('I need amount to withdraw')
        return
    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[0]
    else:
        try:
            amount = int(amount)
        except:
            await ctx.send('please put a number or all')
            return
        if amount > bal[0]:
            await ctx.send('You don\'t have that much money!')
            return
        if amount < 0:
            await ctx.send('Amount must be positive!')
            return
    await update_bank(ctx.author, -1 * amount)
    await update_bank(ctx.author, amount, 'bank')
    await ctx.send(f'You deposited {amount} dollars')


@client.command(aliases=['pay', 'give'])
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)
    if amount is None:
        await ctx.send('I need amount to withdraw')
    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[0]
    else:
        try:
            amount = int(amount)
        except:
            await ctx.send('please put a number or all')
            return
        if amount > bal[0]:
            await ctx.send('You don\'t have that much money!')
            return
        if amount < 0:
            await ctx.send('Amount must be positive!')
            return
    await update_bank(ctx.author, -1 * amount)
    await update_bank(member, amount)
    await ctx.send(f'You sent {amount} dollars')


@client.command(aliases=['slot'])
async def slots(ctx, amount=None):
    await open_account(ctx.author)
    if amount is None:
        await ctx.send('I need amount to withdraw')
    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[0]
    else:
        try:
            amount = int(amount)
        except:
            await ctx.send('please put a number or all')
            return
        if amount > bal[0]:
            await ctx.send('You don\'t have that much money!')
            return
        if amount < 0:
            await ctx.send('Amount must be positive!')
            return
    final = []
    bag = await open_bag(ctx.author)
    for i in range(3):
        a = random.choice(['X', 'C', 'Q'])
        final.append(a)
    await ctx.send(str(final))
    if final[0] == final[1] == final[2]:
        for item in bag:
            if item['item'] == 'lucky_cat':
                amount = int(amount * 1.5)
                await ctx.send(f'And your cat boosted you!!!')
                break
        await update_bank(ctx.author, amount * 3)
        await ctx.send('You won!')
    elif final == ['X', 'Q', 'C']:
        await ctx.send('Wow lucky')
    else:
        await update_bank(ctx.author, -1 * amount)
        await ctx.send('You lost! :(')


@client.command()
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    bal = await update_bank(member)

    if bal[0] < 50:
        await ctx.send('It\'s not worth it!')
        await ctx.send('You seemed sus and were fined 100 dollars :(')
        await update_bank(ctx.author, -100, 'bank')
        return

    amount = random.randint(1, bal[0])
    await update_bank(ctx.author, amount)
    await update_bank(member, amount * -1)
    await ctx.send(f'You stole {amount} dollars! Run!!!')


@client.command()
async def shop(ctx):
    em = discord.Embed(title='Shop')
    for item in mainshop:
        name = item['name']
        price = item['price']
        desc = item['description']
        em.add_field(name=name, value=f'${price} | {desc}')
    await ctx.send(embed=em)


@client.command()
async def egg(ctx):
    await ctx.send('you ARE EGG')


@client.command()
async def buy(ctx, item, amount=1):
    await open_account(ctx.author)
    res = await buy_this(ctx.author, item, amount)
    if not res[0]:
        if res[1] == 1:
            await ctx.send(f'{item} is not a valid item')
            return
        if res[1] == 2:
            await ctx.send('You don\'t have enough money to buy that!')
            return
    await ctx.send(f'You just bought {amount} {item}')


async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    price = 0
    for item in mainshop:
        name = item['name'].lower()
        if name == item_name:
            name_ = name
            price = item['price']
            break
    if name_ is None:
        return [False, 1]

    cost = price * amount
    users = await get_user_data()
    bal = await update_bank(user)

    if bal[0] < cost:
        return [False, 2]
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]['bag']:
            n = thing['item']
            if n == item_name:
                old_amt = thing['amount']
                new_amt = old_amt + amount
                users[str(user.id)]['bag'][index]['amount'] = new_amt
                t = 1
                break
            index += 1
        if t is None:
            obj = {'item': item_name, 'amount': amount}
            users[str(user.id)]['bag'].append(obj)
    except:
        obj = {'item': item_name, 'amount': amount}
        users[str(user.id)]['bag'] = [obj]
    with open('users info.json', 'w') as f:
        json.dump(users, f)

    await update_bank(user, cost * -1)
    return [True, 'worked']


async def open_bag(user):
    await open_account(user)
    users = await get_user_data()

    try:
        bag = users[str(user.id)]['bag']
    except:
        bag = [{'item': 'NOTHING (poor)', 'amount': 'NONE'}]
    return bag


@client.command(aliases=['invo'])
async def bag(ctx):
    user = ctx.author
    bag = await open_bag(user)
    em = discord.Embed(title='Bag')
    for item in bag:
        name = item['item']
        amount = item['amount']
        em.add_field(name=name, value=amount)

    await ctx.send(embed=em)


@client.command()
async def timer(ctx, seconds):
    try:
        secondint = int(seconds)
        if secondint > 300:
            await ctx.send("I don't think im allowed to do go above 300 seconds.")
            raise BaseException
        if secondint <= 0:
            await ctx.send("I don't think im allowed to do negatives")
            raise BaseException
        message = await ctx.send("Timer: {seconds}")
        while True:
            secondint -= 1
            if secondint == 0:
                await message.edit(content="Ended!")
                break
            await message.edit(content=f"Timer: {secondint}")
            await asyncio.sleep(1)
        await ctx.send(f"{ctx.author.mention} Your countdown Has ended!")
    except ValueError:
        await ctx.send("Must be a number!")


client.run('TOKEN')
