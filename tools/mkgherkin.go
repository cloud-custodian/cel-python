// SPDX-Copyright: Copyright (c) Capital One Services, LLC
// SPDX-License-Identifier: Apache-2.0
// Copyright 2020 Capital One Services, LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and limitations under the License.

package main

/*
    Converts Textproto (or protobuf) SimpleTest documents into Gherkin.

    See go doc github.com/google/cel-spec/proto/test/v1/testpb SimpleTest

    The template emits a Gherkin-formatted Feature with a number of Scenarios.
*/

import (
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"text/template"
	"encoding/json"

	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/encoding/prototext"

	spb "github.com/google/cel-spec/proto/test/v1/testpb"

	// The following are needed to link in these proto libraries
	// which are needed dynamically, despite not being explicitly
	// used in the Go source.
	_ "github.com/google/cel-spec/proto/test/v1/proto2/test_all_types"
	_ "github.com/google/cel-spec/proto/test/v1/proto3/test_all_types"
)

func parseSimpleFile(filename string) (*spb.SimpleTestFile, error) {
	bytes, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	var pb spb.SimpleTestFile
	err = prototext.Unmarshal(bytes, &pb)
	if err != nil {
		return nil, err
	}
	return &pb, nil
}

var json_formatter = protojson.MarshalOptions{
	Multiline:       true,
	UseProtoNames:   false,
	EmitUnpopulated: false,
}

func json_testfile(testFile *spb.SimpleTestFile) {
	fmt.Println(json_formatter.Format(testFile))
}

func gherkin_testfile(testFile *spb.SimpleTestFile) {
    // There are several kinds of "results" for a test.
    //      *SimpleTest_Value -- these become a `Then value is ...` step.
    //      *SimpleTest_EvalError -- these become a `Then eval_error is ...` step.
    //      *SimpleTest_AnyEvalErrors -- these become a `Then eval_error is ...` step.
    //      *SimpleTest_Unknown -- These don't seem to be used
    //      *SimpleTest_AnyUnknowns -- These don't seem to be used

	const test_template = `
Feature: {{.Name}}
         {{.Description}}
{{range .Section}}
# {{.Name}} -- {{.Description}}
{{range .Test}}
Scenario: {{.Name}}
          {{.Description}}

{{- if .DisableMacros}}
   Given disable_macros parameter is {{.DisableMacros}}
{{end}}
{{- if .DisableMacros}}
   Given disable_check parameter is {{.DisableCheck}}
{{end}}
{{- if .TypeEnv}}
{{- range $index, $env := .TypeEnv}}
   Given type_env parameter {{printf "%q" $env.Name}} is {{printf "%v" $env.GetDeclKind}}
{{end -}}
{{end}}
{{- if .Bindings}}
{{- range $key, $value := .Bindings}}
   Given bindings parameter {{printf "%q" $key}} is {{printf "%v" $value.GetValue}}
{{end -}}
{{end}}
{{- if .Container}}
   Given container is {{printf "%q" .Container}}
{{end}}
    When CEL expression {{printf "%q" .Expr}} is evaluated
{{if .GetValue}}    Then value is {{printf "%v" .GetValue}}{{end -}}
{{if .GetEvalError}}    Then eval_error is {{printf "%v" .GetEvalError}}{{end -}}

    {{- /* Then JSON value is {{json .ResultMatcher | printf "%s" */}}

{{end}}
{{end}}
`
	func_map := template.FuncMap{
		"json": json.Marshal,
	}
	gherkin_template := template.Must(template.New("gherkin").Funcs(func_map).Parse(test_template))
	err := gherkin_template.Execute(os.Stdout, testFile)
	if err != nil {
		panic(err)
	}
}

var json_format bool
var gherkin_format bool

func init() {
	flag.BoolVar(&json_format, "json", false, "JSON-format output")
	flag.BoolVar(&gherkin_format, "gherkin", true, "Gherkin-format output")
}

func main() {
	flag.Parse()
	for _, input_file := range flag.Args() {
		fmt.Fprintf(os.Stderr, "Reading %v\n", input_file)
		pb, err := parseSimpleFile(input_file)
		if err != nil {
			panic(err)
		}
		if gherkin_format {
			gherkin_testfile(pb)
		}
		if json_format {
			json_testfile(pb)
		}
	}
}
