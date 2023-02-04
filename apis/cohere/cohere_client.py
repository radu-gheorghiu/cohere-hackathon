import cohere
from cohere.classify import Example


class CohereClient:
    def __init__(self):
        """
        Initialize the Cohere client.

        """
        self.co = cohere.Client("YOUR_API_KEY")

    def embed(self, texts, model="large", truncate="NONE"):
        """
        Embed the list of texts.

        Parameters:
            texts (list[str]): An array of strings for the model to embed
            truncate (str): NONE|START|END, specifies how the API will handle inputs longer than the maximum token length

        Returns:
            list of vectors represint
        """
        embeds = []
        batch_size = 96
        for i in range(0, len(texts), batch_size):
            response = self.co.embed(
                model=model, texts=texts[i : i + batch_size], truncate=truncate
            ).embeddings
            embeds.extend(response)
        return embeds

    def check_comments_are_appropriate(self, texts):
        """
        Check if the comment is appropriate.

        Parameters:
            texts (list): The text to be checked.

        Returns:
            bool: True if the comment is appropriate, False otherwise.
        """
        response = self.co.classify(
            model='large',
            inputs=texts,
            examples=[Example("This is dumb", "inappropriate"), Example("💩", "inappropriate"),
                      Example("This is 💩", "inappropriate"), Example("This is stupid", "negative"),
                      Example("You are ugly", "negative"), Example("This video is beautiful", "appropriate"),
                      Example("This is amazing", "appropriate"), Example("This is horrible", "negative"),
                      Example("Lovely video", "appropriate"), Example(
                    "Edmunds is like conjob reports and is skewing data for tesla.  Also the XLE doesn’t compare to the Tesla, so the real numbers will be better for Tesla.",
                    "neutral"), Example(
                    "It is extremely rare that the batteries ever fail.  Statistically it is more likely to have an ice engine seize up.",
                    "neutral"), Example(
                    "Factor in Toyota reliability, fit and finish, resale and dealer support. Every Tesla I\'ve seen has had horrid quality issues and plagued with constant niggles.",
                    "neutral"), Example(
                    "Not realistic assumptions. Should use Tesla insurance. Should use more like 30k miles per year. Gas price is much higher in California. Most people keep car for more than 5 years. Also what about the cost to the environment and the cost saved to Tesla being a safer car.",
                    "neutral"), Example(
                    "Prius gets 57 mpg. as an owner of two Priuses. Not true and is baloney. oil change every 5k, 2 hours x 15 = 30 hours(75k miles.). Pumping gas once a week, 15 minutes x 52 weeks x 5 years = 65 hours. vs model 3 charge at home and no oil change. 30+65/24=3.95 days. Lost almost four days of time just pumping gas and oil change. Best of all. all Teslas are some of the safest vehicles on the road today. Who is SPAN?",
                    "neutral"), Example("Factor in range, and I’ll go with the Prius", "neutral"),
                      Example("Prius is not the luxury car how can you compare with any tesla", "neutral"), Example(
                    "Great video as usual. Not doubting it drives well, but Mercedes has really messed up the design, don\'t know what\'s happening in their studio but it just looks really really odd. Inside and especially out.",
                    "appropriate"), Example(
                    "Wow, so tiny in the backseats. Very disappointing imo. No car for carrying tall people in the back. Not good for a car that is 4.72 meters long, bad package. But great review as allways thomas!",
                    "neutral"), Example("air suspension???....not for me...", "appropriate"),
                      Example("I remember back in the days Thomas said he was 186cm. Has Thomas grown taller??",
                              "neutral"), Example("I think Mercedes has lost some of it\'s charm", "neutral"),
                      Example("Agreed. This looks less sleek and more boxy mixed with a child’s idea of sporty.",
                              "neutral"), Example(
                    "I think the opposite is the case. Especially the interior has improved quite a bit in style.",
                    "appropriate"), Example(
                    "long ago, the absolute cheap plastic elements they use is shocking, the new GLE headlight knob is so shocking and cheap that I refuse to buy the brand period. Afer 20yrs they have lost me as a customer. I\'m shocked to say that a BMW interior is better quality than Mercedes.",
                    "neutral"), Example("You can say it “ a lot “", "neutral"),
                      Example("Yh Mercedes is no longer sleek", "neutral"), Example(
                    "Front grill looks the cheapest to date on a merc. Interior is full of shiny plastic (piano black), big screens do not look expensive,... Not to speak about the fake exhaust.",
                    "appropriate"), Example(
                    "Mercedes\' cars have, over the years, had many, many attributes. Charm has never been one of them.",
                    "neutral"), Example("Bmw is miles ahead in terms of design and interior", "appropriate"), Example(
                    "A LOT of its charm... The interiors are chasing after the bling-bling market, the opposite of what I associate with the brand. Also, every new incarnation bigger than the last. When will this madness end? If I wanted to be a bus driver I would buy a bus.",
                    "neutral"),
                      Example("Your videos are great thanks for doing this for us all for so long!!! ", "appropriate"),
                      Example("And by the way those people they were making fun of you they’re jealous", "appropriate"),
                      Example(
                          "you know i have a red car and when i\'m wearing green i think to myself i don\'t really go with my car color today.....haha",
                          "neutral"), Example("This is shit", "inappropriate"),
                      Example("The offroad see through camera looks interesting", "appropriate"),
                      Example("Good video.", "appropriate"), Example(
                    "I love German cars.....but Mercedes quality ranking is bad here in America currently; don\'t know if that\'s a domestic production issue or what?",
                    "neutral"), Example(
                    "Lovely car. Won’t buy mercedes though. It’s cheaply made and old Skool brand . Audi and Porsche so much better",
                    "neutral"), Example("Was looking forward to this review!", "appropriate"),
                      Example("This is crap", "negative"), Example("looks like crap", "negative"),
                      Example("how 💩", "negative"), Example("very much 💩", "negative"),
                      Example("a lot of 💩", "negative"), Example("looks horrible", "negative")])
        processed_responses = [comment.prediction for comment in response]
        return processed_responses

    def summarize_comments(self, comments):
        response = self.co.generate(
            model='xlarge',
            prompt=f"""Summarize these comments: 
        '@YearningFoSkins i think Magnus offered a draw',
        'At that time Magnus was having stomach issues so he offered a draw',
        'For anyone confused Magnus had a bad stomach and offered a draw, his opponent accepted it.',
        "For anyone wondering, Magnus' stomach was hurting so he offered a draw and the guy accepted.",
        'What a man accepting the draw so Magnus could go to the bathroom',
        'listen in 00:52 Magnus offered a draw'
        -TLDR: "Magnus had a stomach ache and he offered a draw to Vidit, which his opponent accepted"
        ||
        Summarize these comments:
        never knew Thor is a good chess player
        I didn't know Thor played chess
        Thor playing chess now
        Thor plays chess
        I can't believe Thor can play chess well.
        Damn Thor plays chess?
        Thor play chess? Wow
        -TLDR: "I never knew Thor played chess"
        ||
        Summarize the following comments:
        I don't understand  , why magnus won?
        What just happened? Can someone explain me how did magnus win?
        I don't understand how magnus won that game.
        I dont even understand how magnus won. Anyone pls care to explain
        -TLDR: "I don't understand what happened. Did Magnus win?"
        ||
        Summarize the following comments:
        Whose here only because they watched The Queen’s Gambit?
        Who’s here after watching The Queen’s Gambit?
        Who’s here after watching the Queen’s Gambit?
        Who else is here after watching The Queen's Gambit?
        -TLDR: "Who's here because of the Queen's Gambit?"
        ||
        Summarize the following comments:
        Wow almost as crazy as YouTube’s recommended algorithm.
        YouTube algorithm blessed us again.
        The youtube algorithm just does what it wants these days ;-;
        Well you can blame YouTube algorithm but it brought us together again
        YouTube algorithm is something
        YouTube algorithm...you ruinous bitch.
        Thank you YouTube algorithm, very cool
        YouTube algorithm has brought us together once again.
        Lol looks like youtube algorithm fucked up again
        YouTube algorithm don’t even care at this point
        YouTube algorithm doing what he does the best
        Thanks YouTube Algorithm
        I see Youtube's algorithm brought us together again
        Love the YouTube algorithm
        Well I don't know why the youtube algorithm brought me here, but it is odd.
        Thanks algorithm! very cool!
        Wtf this Youtube algorithm is drunk.
        YouTube algorithm is crazy
        Damm, the youtube algorithm is going crazy rn
        YouTube algorithm at it again...
        Gotta love the youtube algorithm
        Ok, first of all, because of YouTube algorithm.....
        Thank's youtube Algorithm that's very interesting
        Ok YouTube algorithm. You must have had a long night.
        YouTube algorithm
        The YouTube algorithm brought me here.
        Here we are gathered by YouTube algorithm again
        Ahh the mysterious YouTube algorithm has brought me here today
        Here because of YouTube's algorithm..
        YouTube’s algorithm at its finest
        Thats it? Youtube algorithm? Why you do this
        -TLDR: "I'm here because of the Youtube algorithm"
        ||
        Summarize these comments:
        Why he didn't just move his King up? We still don't know
        Why couldn’t he just move his king to the side?
        Someone ought to tell him that kings can’t move like that
        Could he jus not move his queen and then save the rook
        What? How? He could have just move his king
        Come on.....he could hai moved the king one step ahead
        Why he moves the king at the end? 😩
        He had one option left he can move his king one step forward
        He can move the king and everything will be okay
        He could move his king 🙄
        why couldn't he just move the king forward
        he can move king to the leftside
        Why didnt he just move his king up?
        Bruh if he moved his king forward one he could have continued the game
        Why didn’t he just move the king forward? 🤨🧐
        Well he can just move the king forward
        He got many options to save the king 🤔🤔
        Couldn’t he have just move the king forward?
        -TLDR: "Why didn't Magnus just move his King?"
        ||
        Summarize these comments:
        {comments}
        -TLDR:
        """,
            max_tokens=100,
            temperature=0.3,
            k=3,
            p=0,
            frequency_penalty=1,
            presence_penalty=0,
            stop_sequences=["||"],
        )
        comments_summary = response.generations[0].text.replace('||', '')
        return comments_summary
