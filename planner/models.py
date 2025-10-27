import random
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class DietTypeChoices(models.TextChoices):
    CLASSIC = 'classic', 'Классическое'
    LOW_CARB = 'low_carb', 'Низкоуглеводное'
    VEGETARIAN = 'vegetarian', 'Вегетарианское'
    KETO = 'keto', 'Кето'


class MealTypeChoices(models.TextChoices):
    BREAKFAST = 'breakfast', 'Завтраки'
    LUNCH = 'lunch', 'Обеды'
    DINNER = 'dinner', 'Ужины'
    DESSERT = 'dessert', 'Десерты'


class Allergy(models.Model):
    name = models.CharField(
        'Аллергия',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Аллергия'
        verbose_name_plural = 'Аллергии'

    def __str__(self):
        return self.name


class SubscriptionPlan(models.Model):
    DURATION_CHOICES = (
        (1, '1 месяц'),
        (3, '3 месяца'),
        (6, '6 месяцев'),
        (12, '12 месяцев'),
    )
    duration = models.IntegerField(
        'Срок подписки',
        choices=DURATION_CHOICES,
        default=1,
        unique=True,
        db_index=True,
    )
    breakfast_price = models.DecimalField(
        'Цена подписки на завтраки',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    lunch_price = models.DecimalField(
        'Цена подписки на обеды',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    dinner_price = models.DecimalField(
        'Цена подписки на ужины',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    dessert_price = models.DecimalField(
        'Цена подписки на десерты',
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    class Meta:
        verbose_name = 'Тарифный план'
        verbose_name_plural = 'Тарифные планы'

    def __str__(self) -> str:
        return f"{self.get_duration_display()} "

    @classmethod
    def get_duration_display_by_value(cls, duration_value):
        choices_dict = dict(cls.DURATION_CHOICES)
        return choices_dict.get(duration_value, 'Неизвестно')

    def get_price_by_meal_type(self, meal_type: MealTypeChoices):
        prices = {
            MealTypeChoices.BREAKFAST: self.breakfast_price,
            MealTypeChoices.LUNCH: self.lunch_price,
            MealTypeChoices.DINNER: self.dinner_price,
            MealTypeChoices.DESSERT: self.dessert_price,
        }
        return prices.get(meal_type, 0)

    def total_price(self, selected_meal_types: list[MealTypeChoices]):
        total = Decimal('0')
        for meal_type in selected_meal_types:
            total += self.get_price_by_meal_type(meal_type)
        return total


class UserSubscription(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscription',
    )
    diet_type = models.CharField(
        'Тип диеты',
        choices=DietTypeChoices.choices,
        db_index=True,
    )
    allergies = models.ManyToManyField(
        Allergy,
        blank=True,
        verbose_name='Аллергии',
    )
    selected_meal_types = models.JSONField(
        'Выбранные приёмы пищи',
        default=list,
    )
    persons_count = models.IntegerField(
        'Количество персон',
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        default=1,
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.RESTRICT,
        verbose_name='Тарифный план',
    )
    start_date = models.DateField(
        'Дата начала подписки',
        auto_now_add=True,
    )
    end_date = models.DateField(
        'Дата окончания подписки',
    )

    class Meta:
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'

    def __str__(self):
        return f"Подписка {self.user.username}"

    @property
    def is_active(self):
        return self.end_date >= timezone.now().date()

    @property
    def total_price(self):
        return self.plan.total_price(self.selected_meal_types) * self.persons_count

    @property
    def meals_count(self):
        return len(self.selected_meal_types)

    @property
    def has_allergies(self):
        return self.allergies.exists()

    def get_allergies_list(self):
        return list(self.allergies.values_list('name', flat=True))


def get_unique_filename(filename: str) -> str:
    extension = filename.rsplit('.', 1)[-1].lower()
    return f'{uuid.uuid4().hex}.{extension}'


def get_avatar_upload_path(instance, filename: str) -> str:
    return f'avatars/{get_unique_filename(filename)}'


class UserProfile(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='profile',
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to=get_avatar_upload_path,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.user.username


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('g', 'Граммы'),
        ('ml', 'Миллилитры'),
        ('pcs', 'Штуки'),
        ('tbsp', 'Столовые ложки'),
        ('tsp', 'Чайные ложки'),
    ]
    name = models.CharField(
        'Название ингредиента',
        max_length=150,
    )
    allergens = models.ManyToManyField(
        Allergy,
        blank=True,
        verbose_name='Аллергены',
    )
    calories = models.DecimalField(
        'Калорийность',
        max_digits=7,
        decimal_places=2,
    )
    unit = models.CharField(
        'Единица измерения',
        max_length=10,
        choices=UNIT_CHOICES,
        default='g',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.get_unit_display()})'


def get_dish_upload_path(instance, filename: str) -> str:
    return f'dishes/{get_unique_filename(filename)}'


class DishManager(models.Manager):
    def get_dishes_for_subscription(self, subscription):
        return self.filter(
            diet_type=subscription.diet_type,
            category__in=subscription.selected_meal_types,
        ).exclude(
            ingredients__allergens__in=subscription.allergies.all(),
        ).distinct()


class Dish(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    ]
    name = models.CharField(
        'Название блюда',
        max_length=150,
    )
    description = models.TextField(
        'Описание блюда',
    )
    recipe = models.TextField(
        'Рецепт приготовления',
        blank=True,
        default='',
    )
    photo = models.ImageField(
        'Фото блюда',
        blank=True,
        null=True,
        upload_to=get_dish_upload_path,
    )
    diet_type = models.CharField(
        'Тип меню',
        choices=DietTypeChoices.choices,
        default=DietTypeChoices.CLASSIC,
        db_index=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='DishIngredient',
        verbose_name='Ингредиенты',
    )
    category = models.CharField(
        'Категория блюда',
        max_length=50,
        choices=MealTypeChoices.choices,
        default=MealTypeChoices.LUNCH,
        db_index=True,
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин)',
        default=30,
        help_text='Время в минутах',
    )
    difficulty = models.CharField(
        'Сложность приготовления',
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
    )
    portions = models.PositiveIntegerField(
        'Количество порций',
        default=1,
        help_text='На сколько персон рассчитано блюдо',
    )

    objects = DishManager()

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        indexes = [
            models.Index(fields=['diet_type', 'category']),
        ]

    def __str__(self):
        return self.name

    @property
    def total_calories(self):
        total = Decimal('0')
        for di in self.dishingredient_set.select_related('ingredient').all():
            total += di.ingredient.calories * di.quantity
        return total.quantize(Decimal('0.01'))

    @property
    def calories_per_portion(self):
        if self.portions > 0:
            return (self.total_calories / self.portions).quantize(Decimal('0.01'))
        return Decimal('0')

    @property
    def is_vegetarian(self):
        non_veg_keywords = ['мясо', 'куриц', 'говядин', 'свинин', 'баранин', 'рыб', 'морепродукт']
        return not any(keyword in self.name.lower() or
                       any(keyword in ing.name.lower() for ing in self.ingredients.all())
                       for keyword in non_veg_keywords)

    def get_ingredients_list(self):
        return [
            {
                'name': di.ingredient.name,
                'quantity': di.quantity,
                'unit': di.ingredient.get_unit_display(),
                'calories': (di.ingredient.calories * di.quantity).quantize(Decimal('0.01')),
            }
            for di in self.dishingredient_set.select_related('ingredient').all()
        ]


class DishIngredient(models.Model):
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    quantity = models.DecimalField(
        'Количество',
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'Ингредиент блюда'
        verbose_name_plural = 'Ингредиенты блюд'
        unique_together = ['dish', 'ingredient']

    def __str__(self):
        return f'{self.ingredient.name} - {self.quantity} {self.ingredient.get_unit_display()}'

    @property
    def total_calories(self):
        return (self.ingredient.calories * self.quantity).quantize(Decimal('0.01'))


class DailyMenu(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='daily_menus',
    )
    date = models.DateField(
        'Дата меню',
        default=timezone.now,
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Дневное меню'
        verbose_name_plural = 'Дневные меню'
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Меню {self.user.username} на {self.date}"

    @property
    def total_calories(self):
        total = Decimal('0')
        for meal in self.meals.select_related('dish').all():
            total += meal.dish.total_calories
        return total.quantize(Decimal('0.01'))

    @property
    def total_cooking_time(self):
        total = 0
        for meal in self.meals.select_related('dish').all():
            total += meal.dish.cooking_time
        return total

    @property
    def meals_count(self):
        return self.meals.count()

    @classmethod
    def generate_for_user(cls, user):
        if not hasattr(user, 'subscription') or not user.subscription.is_active:
            return None

        subscription = user.subscription
        today = timezone.now().date()
        cls.objects.filter(user=user, date=today).delete()
        daily_menu = cls.objects.create(user=user, date=today)

        available_dishes = Dish.objects.get_dishes_for_subscription(subscription)

        for meal_type in subscription.selected_meal_types:
            meal_dishes = available_dishes.filter(category=meal_type)
            if meal_dishes.exists():
                selected_dish = random.choice(list(meal_dishes))
                DailyMeal.objects.create(
                    daily_menu=daily_menu,
                    meal_type=meal_type,
                    dish=selected_dish,
                )

        return daily_menu

    @classmethod
    def get_todays_menu_for_user(cls, user):
        if not hasattr(user, 'subscription') or not user.subscription.is_active:
            return None

        try:
            today = timezone.now().date()
            return cls.objects.get(user=user, date=today)
        except cls.DoesNotExist:
            return cls.generate_for_user(user)

    @classmethod
    def get_todays_menu_with_dishes(cls, user):
        daily_menu = cls.get_todays_menu_for_user(user)
        if daily_menu:
            meals_dict = {
                meal.meal_type: meal.dish
                for meal in daily_menu.meals.select_related('dish').all()
            }
            return {
                'menu': daily_menu,
                'meals': meals_dict,
            }
        return None

    def get_meals_by_type(self):
        return {meal.meal_type: meal.dish for meal in self.meals.select_related('dish').all()}


class DailyMeal(models.Model):
    daily_menu = models.ForeignKey(
        DailyMenu,
        on_delete=models.CASCADE,
        verbose_name='Дневное меню',
        related_name='meals',
    )
    meal_type = models.CharField(
        'Тип приема пищи',
        max_length=20,
        choices=MealTypeChoices.choices,
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        verbose_name='Блюдо',
    )

    class Meta:
        verbose_name = 'Прием пищи'
        verbose_name_plural = 'Приемы пищи'
        unique_together = ['daily_menu', 'meal_type']
        ordering = ['meal_type']

    def __str__(self):
        return f"{self.get_meal_type_display()} - {self.dish.name}"

    @property
    def calories(self):
        return self.dish.total_calories

    @property
    def cooking_time(self):
        return self.dish.cooking_time
