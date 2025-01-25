grammar Varphi;

// Parser rules
program : line* EOF;
line : STATE TAPE_CHARACTER STATE TAPE_CHARACTER HEAD_DIRECTION;

// Lexer rules
fragment LEFT : 'L';
fragment RIGHT : 'R';
fragment TALLY : '1';
fragment BLANK : '0';

STATE : 'q'[a-zA-Z0-9_]+;
TAPE_CHARACTER : TALLY | BLANK;
HEAD_DIRECTION : LEFT | RIGHT;

// Single-line comment (starts with // and ends at the end of the line)
COMMENT : '//' ~[\r\n]* -> skip;

// Multi-line comment (starts with /* and ends with */, can span multiple lines)
MULTI_COMMENT : '/*' .*? '*/' -> skip;

// Skip unnecessary whitespaces
WHITESPACE : [ \t\r\n]+ -> skip;