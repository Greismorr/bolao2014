from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings


class MyAccountManager(BaseUserManager):
    def create_user(self, username, firstname, lastname, password=None):
        if not username:
            raise ValueError('Você precisa inserir um nome de usuário.')
        if not firstname:
            raise ValueError('Você precisa inserir seu nome.')
        if not lastname:
            raise ValueError('Você precisa inserir seu sobrenome.')

        user = self.model(
            username=username,
            firstname=firstname,
            lastname=lastname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, firstname, lastname, password):
        user = self.create_user(
            username=username,
            password=password,
            firstname=firstname,
            lastname=lastname,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    credits = models.PositiveIntegerField(default=10)

    # A variavel money_won existe para separar o dinheiro ganho com apostas dos créditos que possam ter sido dados
    # por administradores.

    money_won = models.IntegerField(default=0)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Bet(models.Model):
    bettor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    game_name = models.CharField(max_length=28)
    goals_team_one = models.PositiveIntegerField(default=0)
    goals_team_two = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.game_name

class Game(models.Model):
    round = models.CharField(max_length=24, default="Quartas de Final")
    team_one = models.CharField(max_length=24)
    goals_team_one = models.PositiveIntegerField(default=0)
    team_two = models.CharField(max_length=24)
    goals_team_two = models.PositiveIntegerField(default=0)
    game_ended = models.BooleanField(default=False)
    winner = models.CharField(max_length=28, default="Aposta Ainda Não Finalizada")
    last_day = models.DateField()
    ended_in = None

    def __str__(self):
        return self.team_one + " X " + self.team_two

    #Conta a quantidade de apostadores vencedores e diz se o jogo empatou ou não.
    def check_winner_and_result(self, bets):
        there_is_winner = 0
        winners = 0

        if self.goals_team_one > self.goals_team_two or self.goals_team_two > self.goals_team_one:
            self.ended_in = "win"

            for bet in bets:
                if bet.goals_team_one == self.goals_team_one and bet.goals_team_two == self.goals_team_two:
                    winners += 1

            if winners == 0:
                for bet in bets:
                    if bet.goals_team_one > bet.goals_team_two and self.goals_team_one > self.goals_team_two:
                        winners += 1

                    elif bet.goals_team_two > bet.goals_team_one and self.goals_team_two > self.goals_team_one:
                        winners += 1

        else:
            self.ended_in = "draw"

            for bet in bets:
                if bet.goals_team_one == self.goals_team_one and bet.goals_team_two == self.goals_team_two:
                    there_is_winner += 1
                    winners += 1
                elif bet.goals_team_one == bet.goals_team_two and there_is_winner == 0:
                    winners += 1
        return winners

    #Adiciona créditos à conta
    def add_credits(self, account, winners, bets_count):
        if winners == 0:
            account.credits += 5
        else:
            prize = bets_count * 5 / winners

            account.money_won += prize
            account.credits += prize
        account.save()

    #Diz qual das duas equipes venceu a partida
    def set_winner(self):
        if self.goals_team_one > self.goals_team_two:
            self.winner = self.team_one

        elif self.goals_team_one < self.goals_team_two:
            self.winner = self.team_two

        else:
            self.winner = "Empate"

    def save(self, *args, **kwargs):
        if self.game_ended:
            self.set_winner()
            bets = list(Bet.objects.filter(game_name=self.__str__()))
            winner_exact_draw = 0
            winners = self.check_winner_and_result(bets)

            #Se ninguém ganhar, os créditos são retornados.
            if winners == 0:
                for bet in bets:
                    account = Account.objects.get(username=bet.bettor)
                    self.add_credits(account, winners, float(len(bets)))

            #Distribui o valor do prêmio.
            for bet in bets:
                if self.ended_in == "win":
                    if bet.goals_team_one == self.goals_team_one and bet.goals_team_two == self.goals_team_two:
                        account = Account.objects.get(username=bet.bettor)
                        print(self.ended_in)
                        print("A")
                        print(account)
                        self.add_credits(account, winners, float(len(bets)))

                    elif bet.goals_team_one > bet.goals_team_two and self.winner == self.team_one:
                        account = Account.objects.get(username=bet.bettor)
                        print(self.ended_in)
                        print("B")
                        print(account)
                        self.add_credits(account, winners, float(len(bets)))

                    elif bet.goals_team_two > bet.goals_team_one and self.winner == self.team_two:
                        account = Account.objects.get(username=bet.bettor)
                        print(self.ended_in)
                        print("C")
                        print(account)
                        self.add_credits(account, winners, float(len(bets)))

                else:
                    for element in bets:
                        if bet.goals_team_one == self.goals_team_one and bet.goals_team_two == self.goals_team_two:
                            account = Account.objects.get(username=bet.bettor)
                            print(self.ended_in)
                            print(account)
                            print("D")
                            winner_exact_draw = 1
                            self.add_credits(account, winners, float(len(bets)))

                    if bet.goals_team_one != self.goals_team_one and bet.goals_team_one == bet.goals_team_two and \
                            winner_exact_draw == 0:
                        account = Account.objects.get(username=bet.bettor)
                        print(self.ended_in)
                        print(account)
                        print("E")
                        self.add_credits(account, winners, float(len(bets)))

            Bet.objects.filter(game_name=self.__str__()).delete()
        super(Game, self).save(*args, **kwargs)










