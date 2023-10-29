import os
import random
import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from dotenv import load_dotenv



load_dotenv()

class Bot:
    """This is a bot that will tell you some killer jokes. 
    Under the hood LLM (gpt) is extensively used with instruction prompt technique 
    to give the bot some sort of characteristics.
    """
    
    def __init__(self,):
       self.api_key = os.getenv('OPENAI_API_KEY')
       self.joke_contexts = ['science', 'politics',  'AI', 'celebrities', 'recent events', 'affairs']
       self.llm = ChatOpenAI(openai_api_key=self.api_key, model='gpt-3.5-turbo', temperature=0.7)
       random.seed()
       
    def is_safe(func):
        """This a decorator function which checks if the provided joke is offensive 
        in nature. Although gpt can not produce any offensive joke I am putting the
        check for other open source model that might not follow such guide lines.
        
        this decorator uses chatGPT with instruction based prompting to check the joke. If the provided 
        joke is offensive we ask for another joke recursively.

        Args:
            func (): this should be tell_joke() function which returns a string.
        """        
        def inner(self):
            joke = func(self)
            messages = [
            SystemMessage(content="Is provided sentence is offensive. '{joke}' just say yes or no "),
            HumanMessage(content=joke)
            ]
            not_safe = self.llm(messages)
            
            if not_safe.content.lower() == "no":
                return joke
            else:
                inner(self)
                
        return inner
       
    def ask_gpt(self, human_message: str, system_message: str)-> str:
        """This is an API method that returns gpt response based on human message
        and system prompt.

        Args:
            human_message (str): user question or instructions
            system_message (str): system prompt(in this bot we mostly use instruction style prompting)

        Returns:
            str: gpt response
        """        
        messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=human_message)
        ]
        ai_message = self.llm(messages=messages)
        return ai_message.content
    
    @is_safe
    def tell_joke(self)->str:
        """This method returns a joke based on the contexts provided in init().
        It chooses the context at random and makes a joke on it. is_safe decorator
        checks if the provided joke is safe or not.
        
        we use system prompt with instruction to only provide the joke.

        Returns:
            str: joke
        """       
        rand_idx = random.randint(0, len(self.joke_contexts)-1)
        joke_context = self.joke_contexts[rand_idx]
        
        system_message = f"Provide a  joke about {joke_context} without any phrasing."
        human_message = "Tell me a joke."
        
        return self.ask_gpt(human_message, system_message)
        
        
    def rate_joke(self, joke: str):
        """This method rates a joke by using the LLM. Base rating
        is taken from the LLM by providing the joke based on the judging_criteria. Then
        we use our weight matrix to find the weighted average(we wanna impose some of our own importance)
        for judging. Again we use instruction style prompting to get the base rating from chatGPT.

        Args:
            joke (str): joke to be rated.
        """        
        judging_criteria = ['Humor', 'Creativity', 'Timeliness', 'Tone and style', 'Delivery style']
        weight_matrix = {
            'Humor': 1, 
            'Creativity': 0.8, 
            'Timeliness':0.6, 
            'Tone and style':0.8, 
            'Delivery style':0.5, 
        }
        messages = [
        SystemMessage(content=f'Rate the joke with scale from 1(not funny) to 10(hilarious) based on the given criteria {",".join(judging_criteria)}. Format your output in json with key as the criteria and value as the rating'),
        HumanMessage(content=f'Is this joke funny? {joke}')
        ]
        base_ratings = json.loads(self.ask_gpt(messages[1],messages[0]))
        
        rating = sum([weight_matrix.get(x)* base_ratings.get(x) for x in judging_criteria])/len(judging_criteria)
        return round(rating)
        

bot = Bot()
joke = bot.tell_joke()
bot.rate_joke(joke)
