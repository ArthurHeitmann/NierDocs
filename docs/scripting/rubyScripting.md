# Ruby Scripting

> This is still very early in development and there are lots of unknowns.

- [Ruby Scripting](#ruby-scripting)
	- [What you need](#what-you-need)
	- [(De-)compiling](#de-compiling)
	- [Basic Code Structure](#basic-code-structure)
	- [Event Triggers](#event-triggers)
	- [Method Naming & Trigger States](#method-naming--trigger-states)
	- [Dialogue & Text Messages](#dialogue--text-messages)
		- [Dialogue Choices](#dialogue-choices)
	- [Interacting with XML actions](#interacting-with-xml-actions)


## What you need

You can download the decompiler and compiler with pre built mruby binaries from [here](https://github.com/ArthurHeitmann/MrubyDecompiler).

Or optionally get the [auto rebuild tool](https://github.com/ArthurHeitmann/NierAutoRebuild).

## (De-)compiling

Drop any rb, mrb or bin files onto the `__init__.py` to (de-)compile them.

I recommend unpacking all dat files in cpk002/cpk012 and using the decompile all option on these folders. That way you can search through many files for examples. p100/p200/p300.dat have a ton of scripting logic that can be interesting.

2 side notes:

For `global_5be16b92_scp.bin` there are 2 warnings during decompilation (unhandled `JMP` codes). The `global_*_scp.bin` files have somewhat complex code. The decompiled outputs might not be 100% correct. For those files, recompiling might cause problems. 

The decompiler adds `self` to all function calls. This can probably be omitted.

## Basic Code Structure

```ruby
proxy = ScriptProxy.new()
class << proxy
	# dialogue text and scripting logic

	def update()
		# setup event triggers
	end
end
Fiber.new() { proxy.update() }
```

## Event Triggers

```ruby
	def fountain_npc_ON_TALK_u0()
		# logic
	end

	def update()
		self.event_trigger("fountain_npc_ON_TALK/u0", "fountain_npc", "ON_TALK")
	end
```

`fountain_npc` is a variable passed from the XML `ScriptAction`. This will will trigger the `fountain_npc_ON_TALK_u0()` method when you talk with `fountain_npc`, with the initial state of `u0`.

## Method Naming & Trigger States

Methods called by trigger events have the following naming structure: `<sourceObject>_<trigger>_<state>`.

Let's say you want to change the dialogue the next time you talk with an NPC. For that you update the trigger state.

```ruby
	def fountain_npc_ON_TALK_q0()
		# on next ON_TALK event, q1 is the initial state
		self.set_trigger_state("q1")
		# This will call fountain_npc_ON_TALK_q1()
		self.call("q1")
	end
```

You can also change the trigger state of another trigger

```ruby
	def this_enemy_dead_a0()
		self.set_trigger_state("fountain_npc/ON_TALK/q0")
	end
```

You can also call ruby functions from the xml

```XML
<action>
	<code str="SendCommand">0xa10e3dbc</code>
	<name>...</name>
	<id>0x3ddd0ba1</id>
	<attribute>0x0</attribute>
	<puid>
		<code str="hap::Action">0xa6aaf7a4</code>
		<id>0x5145d57d</id> <!-- ScriptAction action id -->
	</puid>
	<command>
		<label>Action.signal</label>
	</command>
	<args>&quot;on_chest_opened 0&quot;</args>
</action>
```

```ruby
	def this_on_chest_opened_a0()
		# logic
	end

	def update()
		self.event_trigger("this_on_chest_opened/a0", "this", "on_chest_opened")
	end
```

## Dialogue & Text Messages

```ruby
	M3010_S0020_G0082_001_pod042 = [
		"荳肴",
		"Unknown.",
		"Rﾃｩponse indﾃｩterminﾃｩe.",
		"Informazione non disponibile.",
		"Unbekannt.",
		"Desconocido.",
		"ｶ壱ｪ",
		"荳肴"
	]

	self.automess_ex([
		:M3010_S0020_G0082_001_pod042	# pod042 will speak this
	])
```

All text messages are in 8 languages. The _xyz suffix is used as a hint for who is the one talking. Otherwise the naming doesn't matter. If the variable name matches an existing audio file in the game, it will be played alongside. 

There are different methods for different text types:  
`automess_ex` for speaking  
`mess_ex` for text dialogue  
`sele_ex` for multiple choice text dialogue  
`sysmess_ex` for system messages

### Dialogue Choices

`sele_ex` takes several parameters and returns the index of the selected option.

```ruby
# approximate signature
def sele_ex(dialogue, choices, nextStates, moreSelectionOptions, ...)


# Example:
sele_ex(
	[ :firstMessage, :secondMessage ], # first these messages are displayed
	[ :option1, :option2, :option3 ], # then these 3 choices are available after the last message
	[ "a0", "a1", "nop" ], # for each choice you can specify a next state, "nop" doesn't do anything (no operation)
	[ nil, nil, [ :backclose ] ] # (optional) when clicking back, it will select the 3rd option
)
```

## Interacting with XML actions

You can pass entities or action to the ruby script via the `<variables>` properties. You can access them by calling them like functions. Actions can be enabled/disabled/reset with `self.enable(self.action())`. If you have an action you don't want executed automatically in the XML and only called from ruby, set the `<attribute>` to `0x2`. Command actions can be called by just calling them as functions.
