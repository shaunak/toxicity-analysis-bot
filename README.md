# toxcicity_scorer_bot

This reddit bot will read all the comments of a user, use googles Perspective API to analzye each one for toxicity, and return 
the average score (more data to come) as a reply.


This is a bot that is in beta. Currently is just a personal use script and will only operate on /r/bottesting.

In the future, I want this bot to be able to use googles perspective API to analyze all kinds of things, not just toxicity and also hopefully contribute to the dataset.


Theres still a LOT to be done here:
- learn reddit botiquette, and apply here
- ensure that when the bot is called too quickly, the comments that are not replied to are queued and replied to later
- add waits
- make sure calls to the api doesnt exceed limit/find out what limit is
- make the bot not a personal use script and put it online
- (maybe) make the user summary return as a personal message as opposed to a public comment


Some things (i want) to do with this bot:
- analyze toxicity ratings of left leaning and right leaning subreddits. Is one side more toxic than the other? 
- See what video game communities are more toxic than others
- are toxic comments always downvoted? in what contexts are they downvoted/upvoted ?
