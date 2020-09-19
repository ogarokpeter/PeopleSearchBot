# Telegram bot for coordination of the search of people kindapped by Russian police

## Description

Tegeram bot address: @DEVovdsearchbot (inactive).

We in Russia sometimes find out that our friend or colleague has disappeared and doesn't answer the phone or in social networks. Usually it happens not because of any criminal activity but because she/he has been kidnapped by the police in order to perform some investigation or simply to intimidate the person. Of course, the police never provides anyone, even the relatives, any information about it. So the only way to find the person is to call to every police station in the neighborhood and explicitly ask, 'Do you have detained the guy?'. Sometimes there are tens of these police stations, and they don't always answer the phone, so the search happens much faster when many people are calling to different police stations simultaneously. But then another problem arises: how can we ensure that nobody is wasting time and calling to the police station somebody else has already called? The bot helps to cope with that.

When somebody understands that some guy is lost, she/he adds this guy's name and the neighborhood to the database via the bot. The bot creates 'tasks' in the form of 'Call to the given police station via a given phone number' using its internal police stations database. Any volunteer can take such task (and after the task is taken, the bot secures it in order not to give the same task to anyone else) and submit the results of it (whether the guy is found in the police station or not) to the bot. The bot collects this information and creates new tasks until the guy is found or there are no police stations left.

Current limitations: the police stations database is only for Moscow, and also any Telegram user can create searches and take tasks (no authorization required)

Plans:
- Add police stations from other regions
- Implement some kind of authorization for searchers
- More granular statuses of searches - sometimes police stations refuse to tell whether they have a detained guy or not, and so on.

The bot was developed during the [I Online hackathon in support of political prisoners in Russia](https://github.com/developers-against-repressions/devs-against-the-machine/).

## How to run

The bot requires authorization from Telegram that can be acquired via a Telegram Developer account. You need to get sequrity keys.

To make a bot alive, run

```
$ python3 ovdsearch/webapp.py
```

Help is availible inside the bot - just run ```/help```
