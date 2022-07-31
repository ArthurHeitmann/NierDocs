# XML Scripting

> This is still very early in development and there are lots of unknowns.

- [XML Scripting](#xml-scripting)
	- [What you need](#what-you-need)
	- [What is XML Scripting?](#what-is-xml-scripting)
	- [Useful Actions](#useful-actions)
		- [Area Action](#area-action)
		- [Commands](#commands)
		- [Condition Block](#condition-block)
		- [Entity/Enemy Spawning](#entityenemy-spawning)
		- [Combinations](#combinations)
			- [Area Commands](#area-commands)
			- [Send multiple commands](#send-multiple-commands)
			- [Multi Condition Block](#multi-condition-block)
	- [Some data mining results](#some-data-mining-results)
	- [Things to keep in mind](#things-to-keep-in-mind)

## What you need

Download the PAK & YAX tools from [here](../../tools/pakScriptTools).

Or optionally get the [auto rebuild tool](https://github.com/ArthurHeitmann/NierAutoRebuild).

**Tool usage**

Described [here](../../tools/pakScriptTools/README.md#usage)

I recommend unpacking all dat files in cpk002/cpk012 and running the unpack all script over these folders. That way you can search through many files for examples. p100/p200/p300.dat have a ton of scripting logic that can be interesting. 

## What is XML Scripting?

XML Scripting was originally probably a visual scripting language used by the games engine. Each kind of "block" is an action. All actions are inside the unpacked XML files. Actions can for example place enemies or NPCs, change a quests state, have conditions, disable/enable other actions and much much more.

PAK files are a group of XML files. Inside the 0.xml are groups defined. It's currently not exactly clear what they do. But they can be used as conditions to only execute some XML files under certain conditions. All other XML files have a `<group>` property. Also inside the pakInfo.json each file has a type. What it does is currently unknown.

XML files are executed from top to bottom. `<attribute>`s on `<action>`s can affect the execution flow. There are many different ones, but currently only about 2 or 3 are understood.  
- 0x0 executes the action and immediately moves to the next
- 0x1 and 0x2 seem to not execute it (but can be called from ruby scripts)
- 0x8 blocks the execution flow. For example if you add a timer action, it will wait for X seconds.


```XML
<action>
	<code str="PositionSet">0xe300079d</code>
	<name eng="Position set">ポジションセット</name>
	<id>0x9301bb2f</id>
	<attribute>0x0</attribute>
	<location>
		<position>273.77 -189.38 691.47</position>
		<rotation>0 0 0</rotation>
	</location>
</action>
```

Here's an example action. Let's take it apart.

`<code>` is a hex hash that identifies what kind of action this is. Inside the `str="..."` is the unhashed version as a hint.

`<name>` is a name you can freely chose. This one is from the developers in Japanese. All Japanese texts are automatically translated inside the `str="..."` attribute.

`<id>` is a unique id for this action. It can be referenced in other places by this id. When choosing an id, you can pretty much use any 8 character long hex code, since the probability of a collision is negligible.

The `0x0` `<attribute>` means normal execution.

Everything after this, is action specific.

## Useful Actions

### Area Action

```XML
<action>
	<code str="AreaAction">0x8cf2e32</code>
	<name eng="Area command">エリアコマンド</name>
	<id>0x7726327c</id>
	<attribute>0x8</attribute>
	<area>
		<size>1</size>
		<value>
			<code str="app::area::BoxArea">0x18cffd98</code>
			<position>279.401855 -195.552292 700.240143</position>
			<rotation>0 0 0</rotation>
			<scale>32.186337 13.195042 13.237457</scale>
			<points>-1 -1 1 -1 1 1 -1 1</points>
			<height>1</height>
		</value>
		<!-- More possible values -->
	</area>
</action>
```

This action will block execution until the player enters the area specified. Many other actions have this built in, in an `<area>` property.

### Commands

```XML
<action>
	<code str="SendCommand">0xa10e3dbc</code>
	<name eng="Send command_se">コマンド送信_se</name>
	<id>0x80343155</id>
	<attribute>0x0</attribute>
	<puid>
		<code str="hap::SceneEntities">0xb1803262</code>
		<id str="player">0x98197a65</id>
	</puid>
	<command>
		<label>Pl0000.onCameraShakeEff</label>
	</command>
	<!-- <args>Optional argument</args> -->
</action>
```

You can call certain commands on different things, like actions, entities, the player and more. For a list of all command labels, see [here](../../tools/pakScriptTools/dataMiningResults/AllLabels.json).

### Condition Block

```XML
<action>
	<code str="ConditionBlock">0x606fe5c4</code>
	<name eng="Conditional block">条件ブロック</name>
	<id>0x40355d54</id>
	<attribute>0x8</attribute>
	<condition>
		<puid>
			<code str="app::EntityLayout">0xd8efbb45</code>
			<id>0x27677101</id> <!-- A chest -->
		</puid>
		<condition>
			<state>
				<label>HACKED</label>
			</state>
			<pred>0</pred>
		</condition>
	</condition>
	<delay>0</delay>
	<bDisable>0</bDisable>
</action>
```

This will block execution until a certain condition is met. The conditions work similar to commands. The list of all condition labels can also be found [here](../../tools/pakScriptTools/dataMiningResults/AllLabels.json). What `<pred>` does is currently unknown.

### Entity/Enemy Spawning

You can place any asset or enemy with an `EntityLayoutAction` or an `EntityLayoutArea` (Similar to LAY files). For random enemy generation use `EnemyGenerator`. You can send commands to entities or have conditions on them, with `<code str="app::EntityLayout">0xd8efbb45</code>` and then the `<id>`.

### Combinations

#### Area Commands

```XML
<action>
	<code str="AreaCommand">0x58534a9e</code>
	<name eng="Area command">エリアコマンド</name>
	<id>0xec5758a4</id>
	<attribute>0x0</attribute>
	<area>
		<size>1</size>
		<value>
			<code str="app::area::BoxArea">0x18cffd98</code>
			<position>289.82959 -117.552292 364.963989</position>
			<rotation>0 0 0</rotation>
			<scale>13.318955 13.195042 16.192425</scale>
			<points>-1 -1 1 -1 1 1 -1 1</points>
			<height>1</height>
		</value>
	</area>
	<puid>
		<code str="hap::Action">0xa6aaf7a4</code>
		<id>0x625d25f9</id>
	</puid>
	<hit>
		<command>
			<label>RESET</label>
		</command>
	</hit>
</action>
```

#### Send multiple commands

```XML
<action>
	<code str="SendCommands">0xd9783e91</code>
	<name eng="Send multiple commands_above">複数コマンド送信_上</name>
	<id>0xd8b2ba15</id>
	<attribute>0x2</attribute>
	<commands>
		<items>
			<size>2</size>
			<value>
				<!-- ... -->
			</value>
			<value>
				<!-- ... -->
			</value>
		</items>
	</commands>
</action>
```

#### Multi Condition Block

```XML
<action>
	<code str="MultiConditionBlock">0xe58b4e99</code>
	<name eng="Condition block list">条件ブロックリスト</name>
	<id>0xa86512ed</id>
	<attribute>0x8</attribute>
	<condition>
		<conditions>
			<size>3</size>
			<value>
				<!-- ... -->
			</value>
			<!-- ... -->
			<!-- ... -->
		</conditions>
		<type>0</type>
	</condition>
	<delay>0</delay>
</action>
```

It's currently unknown whether it's an OR or an AND condition. Probably specified in the `<type>`property. If someone can figure it out, let me know.

## Some data mining results

[Here's](../../tools/pakScriptTools/dataMiningResults) some aggregated data from all the actions used in all the pak files. 

## Things to keep in mind

1. For coordinates Blender uses Z as the up axis and the game uses Y. Remember this for location, rotation and scale. Conversion example:  
   ```
   Blender: X: 1 Y: 2 Z: 3
   Game:    X: 1 Y: 3 Z: -2
   ```
2. Rotation is radians
3. Remember to correctly set all the `<size>` properties
4. Currently any XML attributes (`xyz="..."`) are dropped from the YAX conversion. Only the tags value matters.

